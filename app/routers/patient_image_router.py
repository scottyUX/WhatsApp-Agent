import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)

from app.config.rate_limits import RateLimitConfig, limiter
from app.dependencies.services import PatientImageServiceDep
from app.models.patient_image import PatientImageSubmissionModel
from app.services.patient_image_service import PatientNotFoundError
from app.services.supabase_storage_service import UploadedImage
from app.utils import ErrorUtils

router = APIRouter(
    prefix="/api/patient-images",
    tags=["Patient Images"],
)


@router.post(
    "/",
    response_model=PatientImageSubmissionModel,
    summary="Upload patient profile images",
    description=(
        "Accepts 3–6 images for the specified patient profile, stores them in Supabase, "
        "and records the uploaded bundle for later review."
    ),
)
@limiter.limit(RateLimitConfig.DEFAULT)
async def upload_patient_images(
    request: Request,
    patient_image_service: PatientImageServiceDep,
    patient_profile_id: str = Form(
        ...,
        description="Patient profile identifier (UUID) that owns the uploaded images.",
    ),
    files: List[UploadFile] = File(
        ...,
        description="Between three and six image files (e.g., JPEG/PNG) associated with the patient profile.",
    ),
    analysis_notes: Optional[str] = Form(
        None,
        description="Optional notes or observations to accompany this image submission.",
    ),
) -> PatientImageSubmissionModel:
    try:
        uploads: List[UploadedImage] = []
        for upload in files:
            contents = await upload.read()
            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail=f"Uploaded file {upload.filename or 'unnamed'} is empty.",
                )
            uploads.append(
                UploadedImage(
                    filename=upload.filename or "image.jpg",
                    data=contents,
                    content_type=upload.content_type,
                )
            )

        submission = patient_image_service.upload_submission(
            patient_profile_id=patient_profile_id,
            uploads=uploads,
            analysis_notes=analysis_notes,
        )
        return PatientImageSubmissionModel.model_validate(submission)
    except HTTPException:
        raise
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - convert to HTTP error
        raise ErrorUtils.toHTTPException(exc) from exc


@router.get(
    "/",
    response_model=List[PatientImageSubmissionModel],
    summary="List patient image submissions",
    description=(
        "Returns previously uploaded image bundles. Provide a patient profile ID to scope the results."
    ),
)
@limiter.limit(RateLimitConfig.DEFAULT)
async def list_patient_image_submissions(
    request: Request,
    patient_image_service: PatientImageServiceDep,
    patient_profile_id: Optional[str] = Query(
        None,
        description="Filter results to submissions for this patient profile (UUID).",
    ),
) -> List[PatientImageSubmissionModel]:
    try:
        if patient_profile_id is not None:
            try:
                uuid.UUID(patient_profile_id)
            except ValueError as exc:
                raise HTTPException(
                    status_code=400,
                    detail="patient_profile_id must be a valid UUID.",
                ) from exc

        submissions = patient_image_service.list_submissions(
            patient_profile_id=patient_profile_id,
        )
        return [
            PatientImageSubmissionModel.model_validate(submission)
            for submission in submissions
        ]
    except Exception as exc:  # noqa: BLE001 - convert to HTTP error
        raise ErrorUtils.toHTTPException(exc) from exc
