from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Iterable, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.database.entities import Package


class PackageRepository:
    """Data access helpers for clinic packages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        *,
        include_inactive: bool = False,
    ) -> List[Package]:
        query = self.db.query(Package)
        if not include_inactive:
            query = query.filter(Package.is_active.is_(True))
        return query.order_by(Package.created_at.desc()).all()

    def get_by_id(self, package_id: uuid.UUID) -> Optional[Package]:
        return (
            self.db.query(Package)
            .filter(Package.id == package_id)
            .one_or_none()
        )

    def get_by_ids(self, package_ids: Sequence[uuid.UUID]) -> List[Package]:
        if not package_ids:
            return []
        return (
            self.db.query(Package)
            .filter(Package.id.in_(list(package_ids)))
            .all()
        )

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        currency: str = "EUR",
        is_active: bool = True,
        clinic_id: Optional[uuid.UUID] = None,
        grafts_count: Optional[str] = None,
        hair_transplantation_method: Optional[str] = None,
        stem_cell_therapy_sessions: int = 0,
        airport_lounge_access_included: bool = False,
        airport_lounge_access_details: Optional[str] = None,
        breakfast_included: bool = False,
        hotel_name: Optional[str] = None,
        hotel_nights_included: int = 0,
        hotel_star_rating: int = 0,
        private_translator_included: bool = False,
        vip_transfer_details: Optional[str] = None,
        aftercare_kit_supply_duration: Optional[str] = None,
        laser_sessions: int = 0,
        online_follow_ups_duration: Optional[str] = None,
        oxygen_therapy_sessions: int = 0,
        post_operation_medication_included: bool = False,
        prp_sessions_included: bool = False,
        sedation_included: bool = False,
    ) -> Package:
        package = Package(
            name=name,
            description=description,
            price=price,
            currency=currency,
            is_active=is_active,
            clinic_id=clinic_id,
            grafts_count=grafts_count,
            hair_transplantation_method=hair_transplantation_method,
            stem_cell_therapy_sessions=stem_cell_therapy_sessions,
            airport_lounge_access_included=airport_lounge_access_included,
            airport_lounge_access_details=airport_lounge_access_details,
            breakfast_included=breakfast_included,
            hotel_name=hotel_name,
            hotel_nights_included=hotel_nights_included,
            hotel_star_rating=hotel_star_rating,
            private_translator_included=private_translator_included,
            vip_transfer_details=vip_transfer_details,
            aftercare_kit_supply_duration=aftercare_kit_supply_duration,
            laser_sessions=laser_sessions,
            online_follow_ups_duration=online_follow_ups_duration,
            oxygen_therapy_sessions=oxygen_therapy_sessions,
            post_operation_medication_included=post_operation_medication_included,
            prp_sessions_included=prp_sessions_included,
            sedation_included=sedation_included,
        )
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package

    def save(self, package: Package) -> Package:
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package

    def upsert_many(self, packages: Iterable[Package]) -> List[Package]:
        result = []
        for package in packages:
            self.db.add(package)
            result.append(package)
        self.db.commit()
        for package in result:
            self.db.refresh(package)
        return result

    def delete(self, package_id: uuid.UUID) -> bool:
        """Delete a package and return True if successful."""
        package = self.get_by_id(package_id)
        if package is None:
            return False
        
        self.db.delete(package)
        self.db.commit()
        return True
