from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


clinic_packages = Table(
    "clinic_packages",
    Base.metadata,
    Column(
        "clinic_id",
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "package_id",
        UUID(as_uuid=True),
        ForeignKey("packages.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "assigned_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


class Package(Base):
    """
    Represents an offering that can be attached to one or more clinics.
    """

    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true", default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Clinic relationship (one-to-many: clinic can have multiple packages)
    clinic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True
    )

    # Treatment Specifics
    grafts_count: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hair_transplantation_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stem_cell_therapy_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Travel & Accommodation
    airport_lounge_access_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    airport_lounge_access_details: Mapped[str | None] = mapped_column(String(20), nullable=True)
    breakfast_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hotel_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hotel_nights_included: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hotel_star_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    private_translator_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    vip_transfer_details: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Aftercare & Follow-ups
    aftercare_kit_supply_duration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    laser_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    online_follow_ups_duration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    oxygen_therapy_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    post_operation_medication_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prp_sessions_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sedation_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    clinics: Mapped[List["Clinic"]] = relationship(
        "Clinic",
        secondary="clinic_packages",
        back_populates="packages",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - simple repr helper
        return f"<Package {self.id} ({self.name})>"
