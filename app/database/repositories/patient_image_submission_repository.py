import uuid
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.database.entities import PatientImageSubmission


class PatientImageSubmissionRepository:
    """Data access layer for patient image submissions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _coerce_uuid(self, value: Union[str, uuid.UUID]) -> uuid.UUID:
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))

    def create(
        self,
        *,
        patient_profile_id: Union[str, uuid.UUID],
        image_urls: List[str],
        analysis_notes: Optional[str] = None,
    ) -> PatientImageSubmission:
        submission = PatientImageSubmission(
            patient_profile_id=self._coerce_uuid(patient_profile_id),
            image_urls=image_urls,
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

    def list_all(self) -> List[PatientImageSubmission]:
        return (
            self.db.query(PatientImageSubmission)
            .order_by(PatientImageSubmission.created_at.desc())
            .all()
        )

    def update_analysis(
        self,
        submission_id: Union[str, uuid.UUID],
        analysis_notes: Optional[str],
    ) -> Optional[PatientImageSubmission]:
        submission = (
            self.db.query(PatientImageSubmission)
            .filter(PatientImageSubmission.id == self._coerce_uuid(submission_id))
            .first()
        )
        if not submission:
            return None

        submission.analysis_notes = analysis_notes
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
