import uuid
from typing import List, Optional, Union

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
        gender: Optional[Gender] = None,
        clinic_offer_ids: Optional[List[Union[str, uuid.UUID]]] = None,
        # cal_booking_id: Optional[str] = None,  # TODO: Add after migration
    ) -> PatientProfile:
        """Create a patient profile record."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        offers: Optional[List[uuid.UUID]] = None
        if clinic_offer_ids is not None:
            offers = [uuid.UUID(str(clinic_id)) for clinic_id in clinic_offer_ids]

        patient_profile = PatientProfile(
            user_id=user_id,
            name=name,
            phone=phone,
            email=email,
            location=location,
            age=age,
            gender=gender,
            clinic_offer_ids=offers or [],
            # cal_booking_id=cal_booking_id,  # TODO: Add after migration
        )
        self.db.add(patient_profile)
        self.db.commit()
        self.db.refresh(patient_profile)
        return patient_profile

    def save(self, patient_profile: PatientProfile) -> PatientProfile:
        """Persist changes to an existing patient profile."""
        self.db.add(patient_profile)
        self.db.commit()
        self.db.refresh(patient_profile)
        return patient_profile

    def get_by_id(
        self,
        patient_profile_id: Union[str, uuid.UUID],
    ) -> Optional[PatientProfile]:
        """Fetch a patient profile by its primary key."""
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        return (
            self.db.query(PatientProfile)
            .filter(PatientProfile.id == patient_profile_id)
            .first()
        )

    def get_by_user_id(
        self,
        user_id: Union[str, uuid.UUID],
    ) -> Optional[PatientProfile]:
        """Fetch a patient profile by the owning user ID."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        return (
            self.db.query(PatientProfile)
            .filter(PatientProfile.user_id == user_id)
            .first()
        )

    def add_clinic_offers(
        self,
        patient_profile: PatientProfile,
        clinic_ids: List[uuid.UUID],
    ) -> PatientProfile:
        """Append clinic offers to the patient profile without duplicating entries."""
        existing_ids = set(patient_profile.clinic_offer_ids or [])
        existing_ids.update(clinic_ids)
        patient_profile.clinic_offer_ids = list(existing_ids)
        return self.save(patient_profile)

    def set_clinic_offers(
        self,
        patient_profile: PatientProfile,
        clinic_ids: List[uuid.UUID],
    ) -> PatientProfile:
        """Replace clinic offers on the patient profile."""
        patient_profile.clinic_offer_ids = list(clinic_ids)
        return self.save(patient_profile)
