import uuid
from typing import Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.database.entities import MedicalBackground


class MedicalBackgroundRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        patient_profile_id: Union[str, uuid.UUID], 
        medical_data: Optional[Dict[str, Any]] = None
    ) -> MedicalBackground:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        if medical_data is None:
            medical_data = {}

        medical_background = MedicalBackground(
            patient_profile_id=patient_profile_id,
            medical_data=medical_data
        )
        self.db.add(medical_background)
        self.db.commit()
        self.db.refresh(medical_background)
        return medical_background

    def save(self, medical_background: MedicalBackground) -> MedicalBackground:
        self.db.add(medical_background)
        self.db.commit()
        self.db.refresh(medical_background)
        return medical_background

    def get_by_id(self, medical_background_id: Union[str, uuid.UUID]) -> Optional[MedicalBackground]:
        if isinstance(medical_background_id, str):
            medical_background_id = uuid.UUID(medical_background_id)
        
        return self.db.query(MedicalBackground).filter(MedicalBackground.id == medical_background_id).first()

    def get_by_patient_profile_id(self, patient_profile_id: Union[str, uuid.UUID]) -> Optional[MedicalBackground]:
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        return self.db.query(MedicalBackground).filter(MedicalBackground.patient_profile_id == patient_profile_id).first()
