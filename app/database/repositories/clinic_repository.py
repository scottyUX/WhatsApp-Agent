from __future__ import annotations

import uuid
from typing import List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session

from app.database.entities import Clinic, Package


class ClinicRepository:
    """Query helpers for the clinics domain."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_paginated(
        self,
        *,
        page: int,
        limit: int,
        has_contract: Optional[bool] = None,
    ) -> Tuple[List[Clinic], int]:
        query = self.db.query(Clinic)
        if has_contract is not None:
            query = query.filter(Clinic.has_contract.is_(has_contract))

        total = query.count()
        clinics = (
            query.order_by(Clinic.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return clinics, total

    def get_by_id(self, clinic_id: uuid.UUID) -> Optional[Clinic]:
        return (
            self.db.query(Clinic)
            .filter(Clinic.id == clinic_id)
            .one_or_none()
        )

    def get_by_ids(self, clinic_ids: Sequence[uuid.UUID]) -> List[Clinic]:
        if not clinic_ids:
            return []
        return (
            self.db.query(Clinic)
            .filter(Clinic.id.in_(list(clinic_ids)))
            .all()
        )

    def get_packages(self, clinic: Clinic) -> List[Package]:
        """Get all packages associated with a clinic."""
        return list(clinic.packages)

    def set_packages(
        self,
        clinic: Clinic,
        packages: Sequence[Package],
        *,
        has_contract: Optional[bool] = None,
    ) -> Clinic:
        clinic.packages = list(packages)
        clinic.package_ids = [pkg.id for pkg in packages]

        if has_contract is not None:
            clinic.has_contract = has_contract

        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def update_has_contract(
        self,
        clinic: Clinic,
        has_contract: bool,
    ) -> Clinic:
        clinic.has_contract = has_contract
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic

    def update_fields(
        self,
        clinic: Clinic,
        data: dict,
    ) -> Clinic:
        for key, value in data.items():
            setattr(clinic, key, value)
        self.db.add(clinic)
        self.db.commit()
        self.db.refresh(clinic)
        return clinic
