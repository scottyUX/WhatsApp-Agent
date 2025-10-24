import uuid
from typing import Any, Dict, Iterable, List, Optional, Union

from sqlalchemy.orm import Session

from app.database.entities import PatientImageSubmission


class PatientImageSubmissionRepository:
    """Data access layer for patient image submissions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _coerce_uuid(self, value: Union[str, uuid.UUID]) -> uuid.UUID:
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))

    @staticmethod
    def _normalise_urls(urls: Iterable[str]) -> List[str]:
        return sorted(urls)

    def create(
        self,
        *,
        patient_profile_id: Union[str, uuid.UUID],
        image_urls: List[str],
        analysis: Optional[Dict[str, Any]] = None,
        analysis_notes: Optional[str] = None,
    ) -> PatientImageSubmission:
        submission = PatientImageSubmission(
            patient_profile_id=self._coerce_uuid(patient_profile_id),
            image_urls=image_urls,
            analysis=analysis,
            analysis_notes=analysis_notes,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def list_by_patient_profile(
        self, patient_profile_id: Union[str, uuid.UUID]
    ) -> List[PatientImageSubmission]:
        return (
            self.db.query(PatientImageSubmission)
            .filter(
                PatientImageSubmission.patient_profile_id
                == self._coerce_uuid(patient_profile_id)
            )
            .order_by(PatientImageSubmission.created_at.desc())
            .all()
        )

    def find_by_profile_and_images(
        self,
        *,
        patient_profile_id: Union[str, uuid.UUID],
        image_urls: Iterable[str],
    ) -> Optional[PatientImageSubmission]:
        target = self._normalise_urls(image_urls)
        for submission in self.list_by_patient_profile(patient_profile_id):
            if self._normalise_urls(submission.image_urls) == target:
                return submission
        return None

    def list_all(self) -> List[PatientImageSubmission]:
        return (
            self.db.query(PatientImageSubmission)
            .order_by(PatientImageSubmission.created_at.desc())
            .all()
        )

    def get_latest_by_patient_profile(
        self, patient_profile_id: Union[str, uuid.UUID]
    ) -> Optional[PatientImageSubmission]:
        return (
            self.db.query(PatientImageSubmission)
            .filter(
                PatientImageSubmission.patient_profile_id
                == self._coerce_uuid(patient_profile_id)
            )
            .order_by(PatientImageSubmission.created_at.desc())
            .first()
        )

    def update_analysis(
        self,
        submission_id: Union[str, uuid.UUID],
        analysis: Optional[Dict[str, Any]],
        analysis_notes: Optional[str] = None,
    ) -> Optional[PatientImageSubmission]:
        submission = (
            self.db.query(PatientImageSubmission)
            .filter(PatientImageSubmission.id == self._coerce_uuid(submission_id))
            .first()
        )
        if not submission:
            return None

        submission.analysis = analysis
        submission.analysis_notes = analysis_notes
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
