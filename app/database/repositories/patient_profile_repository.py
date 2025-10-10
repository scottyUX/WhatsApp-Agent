import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import PatientProfile
from app.models.enums import Gender


class PatientProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        user_id: Union[str, uuid.UUID], 
        name: str, 
        phone: str, 
        email: str, 
        location: Optional[str] = None, 
        age: Optional[int] = None, 
        gender: Optional[Gender] = None
    ) -> PatientProfile:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        patient_profile = PatientProfile(
            user_id=user_id,
            name=name,
            phone=phone,
            email=email,
            location=location,
            age=age,
            gender=gender
        )
        self.db.add(patient_profile)
        self.db.commit()
        self.db.refresh(patient_profile)
        return patient_profile

    def save(self, patient_profile: PatientProfile) -> PatientProfile:
        self.db.add(patient_profile)
        self.db.commit()
        self.db.refresh(patient_profile)
        return patient_profile

    def get_by_id(self, patient_profile_id: Union[str, uuid.UUID]) -> Optional[PatientProfile]:
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        return self.db.query(PatientProfile).filter(PatientProfile.id == patient_profile_id).first()

    def get_by_user_id(self, user_id: Union[str, uuid.UUID]) -> Optional[PatientProfile]:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return self.db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
