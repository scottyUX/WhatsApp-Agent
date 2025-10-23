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
        currency: str = "USD",
        is_active: bool = True,
    ) -> Package:
        package = Package(
            name=name,
            description=description,
            price=price,
            currency=currency,
            is_active=is_active,
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
