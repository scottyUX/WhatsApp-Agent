import uuid
from typing import List, Optional, Sequence, Union

from app.database.entities import PatientImageSubmission
from app.database.repositories.patient_image_submission_repository import (
    PatientImageSubmissionRepository,
)
from app.database.repositories.patient_profile_repository import (
    PatientProfileRepository,
)
from app.services.supabase_storage_service import SupabaseStorageService, UploadedImage


class PatientNotFoundError(Exception):
    """Raised when a patient profile cannot be found."""


class PatientImageService:
    """Coordinates patient image uploads and retrieval."""

    def __init__(
        self,
        repository: PatientImageSubmissionRepository,
        profile_repository: PatientProfileRepository,
        storage_service: SupabaseStorageService,
    ) -> None:
        self.repository = repository
        self.profile_repository = profile_repository
        self.storage_service = storage_service

    @staticmethod
    def _validate_upload_count(uploads: Sequence[UploadedImage]) -> None:
        count = len(uploads)
        if count < 3:
            raise ValueError("Please provide at least 3 images.")
        if count > 6:
            raise ValueError("A maximum of 6 images is allowed.")

    def upload_submission(
        self,
        *,
        patient_profile_id: Union[str, uuid.UUID],
        uploads: List[UploadedImage],
        analysis_notes: Optional[str] = None,
    ) -> PatientImageSubmission:
        self._validate_upload_count(uploads)
        try:
            profile_uuid = (
                patient_profile_id
                if isinstance(patient_profile_id, uuid.UUID)
                else uuid.UUID(str(patient_profile_id))
            )
        except ValueError as exc:
            raise ValueError("patient_profile_id must be a valid UUID.") from exc

        patient = self.profile_repository.get_by_id(profile_uuid)
        if not patient:
            raise PatientNotFoundError(f"Patient profile not found: {profile_uuid}")

        image_urls = self.storage_service.upload_patient_images(
            profile_uuid, uploads
        )
        return self.repository.create(
            patient_profile_id=profile_uuid,
            image_urls=image_urls,
            analysis_notes=analysis_notes,
        )

    def list_submissions(
        self,
        *,
        patient_profile_id: Optional[Union[str, uuid.UUID]] = None,
    ) -> List[PatientImageSubmission]:
        if patient_profile_id is not None:
            return self.repository.list_by_patient_profile(patient_profile_id)
        return self.repository.list_all()
