import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from app.database.entities import Offer, PatientProfile


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_profile_id: Union[str, uuid.UUID],
        clinic_ids: List[Union[str, uuid.UUID]],
        package_ids: List[Union[str, uuid.UUID]],
        payment_methods: List[str],
        status: str = "draft",
        notes: Optional[str] = None,
        total_price: Optional[float] = None,
        currency: str = "USD",
        deposit_amount: Optional[float] = None,
        created_by: Optional[Union[str, uuid.UUID]] = None,
        offer_url: Optional[str] = None,
    ) -> Offer:
        """Create a new offer."""
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        clinic_ids_uuids = [
            uuid.UUID(cid) if isinstance(cid, str) else cid
            for cid in clinic_ids
        ]

        package_ids_uuids = [
            uuid.UUID(pid) if isinstance(pid, str) else pid
            for pid in package_ids
        ]

        if isinstance(created_by, str):
            created_by = uuid.UUID(created_by)

        now = datetime.now()
        offer = Offer(
            patient_profile_id=patient_profile_id,
            clinic_ids=clinic_ids_uuids,
            package_ids=package_ids_uuids,
            payment_methods=payment_methods,
            status=status,
            notes=notes,
            total_price=total_price,
            currency=currency,
            deposit_amount=deposit_amount,
            created_by=created_by,
            offer_url=offer_url,
            created_at=now,
            updated_at=now,
        )

        offer.status_history = []

        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def list_paginated(
        self,
        *,
        page: int,
        limit: int,
        patient_profile_id: Optional[Union[str, uuid.UUID]] = None,
        status: Optional[str] = None,
        clinic_id: Optional[Union[str, uuid.UUID]] = None,
        package_id: Optional[Union[str, uuid.UUID]] = None,
        offer_id: Optional[Union[str, uuid.UUID]] = None,
        patient_name: Optional[str] = None,
    ) -> Tuple[List[Offer], int]:
        """Return paginated offers with optional filters."""
        if page < 1:
            page = 1
        if limit < 1:
            limit = 1

        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        if isinstance(clinic_id, str):
            clinic_id = uuid.UUID(clinic_id)
        if isinstance(package_id, str):
            package_id = uuid.UUID(package_id)
        if isinstance(offer_id, str):
            offer_id = uuid.UUID(offer_id)

        query = self.db.query(Offer).options(selectinload(Offer.patient_profile))
        if patient_profile_id:
            query = query.filter(Offer.patient_profile_id == patient_profile_id)
        if status:
            query = query.filter(Offer.status == status)
        if clinic_id:
            query = query.filter(Offer.clinic_ids.contains([clinic_id]))
        if package_id:
            query = query.filter(Offer.package_ids.contains([package_id]))
        if offer_id:
            query = query.filter(Offer.id == offer_id)
        if patient_name:
            trimmed_name = patient_name.strip()
            if trimmed_name:
                ilike_pattern = f"%{trimmed_name}%"
                query = (
                    query.join(PatientProfile, Offer.patient_profile)
                    .filter(PatientProfile.name.ilike(ilike_pattern))
                )

        total = query.count()
        offers = (
            query.order_by(desc(Offer.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return offers, total

    def save(self, offer: Offer) -> Offer:
        """Persist changes to an offer."""
        offer.updated_at = datetime.now()
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_by_id(self, offer_id: Union[str, uuid.UUID]) -> Optional[Offer]:
        """Get an offer by ID."""
        if isinstance(offer_id, str):
            offer_id = uuid.UUID(offer_id)
        return (
            self.db.query(Offer)
            .options(selectinload(Offer.patient_profile))
            .filter(Offer.id == offer_id)
            .first()
        )

    def get_by_patient_profile_id(
        self,
        patient_profile_id: Union[str, uuid.UUID],
    ) -> List[Offer]:
        """Get all offers for a patient."""
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        return (
            self.db.query(Offer)
            .options(selectinload(Offer.patient_profile))
            .filter(Offer.patient_profile_id == patient_profile_id)
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_by_clinic_id(
        self,
        clinic_id: Union[str, uuid.UUID],
    ) -> List[Offer]:
        """Get all offers that include a specific clinic."""
        if isinstance(clinic_id, str):
            clinic_id = uuid.UUID(clinic_id)
        return (
            self.db.query(Offer)
            .options(selectinload(Offer.patient_profile))
            .filter(Offer.clinic_ids.contains([clinic_id]))
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_by_status(self, status: str) -> List[Offer]:
        """Get all offers with a specific status."""
        return (
            self.db.query(Offer)
            .options(selectinload(Offer.patient_profile))
            .filter(Offer.status == status)
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_all(self, limit: int = 100) -> List[Offer]:
        """Get all offers (limited)."""
        return (
            self.db.query(Offer)
            .options(selectinload(Offer.patient_profile))
            .order_by(desc(Offer.created_at))
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        offer_id: Union[str, uuid.UUID],
        new_status: str,
        notes: Optional[str] = None,
        changed_by: Optional[Union[str, uuid.UUID]] = None,
    ) -> Optional[Offer]:
        """Update offer status and append to history."""
        offer = self.get_by_id(offer_id)
        if not offer:
            return None

        if isinstance(changed_by, str):
            try:
                changed_by = uuid.UUID(changed_by)
            except ValueError:
                changed_by = None

        history_entry = {
            "status": new_status,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "changed_by": str(changed_by) if changed_by else None,
        }

        if not isinstance(offer.status_history, list):
            offer.status_history = []
        offer.status_history.append(history_entry)

        offer.status = new_status
        if notes is not None:
            offer.notes = notes

        return self.save(offer)

    def delete(self, offer_id: Union[str, uuid.UUID]) -> bool:
        """Delete an offer."""
        offer = self.get_by_id(offer_id)
        if offer:
            self.db.delete(offer)
            self.db.commit()
            return True
        return False
