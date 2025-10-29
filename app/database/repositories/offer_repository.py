import uuid
from typing import Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.entities import Offer


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_profile_id: Union[str, uuid.UUID],
        clinic_ids: List[Union[str, uuid.UUID]],
        payment_methods: List[str],
        status: str = "draft",
        notes: Optional[str] = None,
        total_price: Optional[float] = None,
        currency: str = "USD",
        deposit_amount: Optional[float] = None,
        created_by: Optional[Union[str, uuid.UUID]] = None,
    ) -> Offer:
        """Create a new offer"""
        # Convert string UUIDs to UUID objects if needed
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        
        clinic_ids_uuids = [
            uuid.UUID(cid) if isinstance(cid, str) else cid 
            for cid in clinic_ids
        ]
        
        if isinstance(created_by, str):
            created_by = uuid.UUID(created_by)

        now = datetime.now()
        offer = Offer(
            patient_profile_id=patient_profile_id,
            clinic_ids=clinic_ids_uuids,
            payment_methods=payment_methods,
            status=status,
            notes=notes,
            total_price=total_price,
            currency=currency,
            deposit_amount=deposit_amount,
            created_by=created_by,
            created_at=now,
            updated_at=now
        )
        
        # Initialize empty status history
        offer.status_history = []
        
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def save(self, offer: Offer) -> Offer:
        """Save an existing offer"""
        offer.updated_at = datetime.now()
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_by_id(self, offer_id: Union[str, uuid.UUID]) -> Optional[Offer]:
        """Get an offer by ID"""
        if isinstance(offer_id, str):
            offer_id = uuid.UUID(offer_id)
        return self.db.query(Offer).filter(Offer.id == offer_id).first()

    def get_by_patient_profile_id(
        self,
        patient_profile_id: Union[str, uuid.UUID]
    ) -> List[Offer]:
        """Get all offers for a patient"""
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        return (
            self.db.query(Offer)
            .filter(Offer.patient_profile_id == patient_profile_id)
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_by_clinic_id(
        self,
        clinic_id: Union[str, uuid.UUID]
    ) -> List[Offer]:
        """Get all offers that include a specific clinic"""
        if isinstance(clinic_id, str):
            clinic_id = uuid.UUID(clinic_id)
        return (
            self.db.query(Offer)
            .filter(Offer.clinic_ids.contains([clinic_id]))
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_by_status(self, status: str) -> List[Offer]:
        """Get all offers with a specific status"""
        return (
            self.db.query(Offer)
            .filter(Offer.status == status)
            .order_by(desc(Offer.created_at))
            .all()
        )

    def get_all(self, limit: int = 100) -> List[Offer]:
        """Get all offers (limited)"""
        return (
            self.db.query(Offer)
            .order_by(desc(Offer.created_at))
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        offer_id: Union[str, uuid.UUID],
        new_status: str,
        notes: Optional[str] = None,
        changed_by: Optional[Union[str, uuid.UUID]] = None
    ) -> Optional[Offer]:
        """Update offer status and add to history"""
        offer = self.get_by_id(offer_id)
        if offer:
            # Add to status history
            if isinstance(offer.status_history, list):
                history_entry = {
                    "status": new_status,
                    "timestamp": datetime.now().isoformat(),
                    "notes": notes,
                    "changed_by": str(changed_by) if changed_by else None,
                }
                offer.status_history.append(history_entry)
            else:
                offer.status_history = [history_entry]
            
            # Update status and notes if provided
            offer.status = new_status
            if notes:
                offer.notes = notes
            
            return self.save(offer)
        return None

    def delete(self, offer_id: Union[str, uuid.UUID]) -> bool:
        """Soft delete an offer (or hard delete if needed)"""
        offer = self.get_by_id(offer_id)
        if offer:
            self.db.delete(offer)
            self.db.commit()
            return True
        return False

