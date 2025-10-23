from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Clinic(Base):
    """
    SQLAlchemy representation of the `clinics` table.

    The table originates from Supabase and already stores most descriptive fields
    (title, contact details, metadata JSON blobs, etc.). We extend it with
    relationship-aware fields used by the application – namely the boolean
    `has_contract` flag and the `package_ids` array that mirrors the packages
    attached through the association table.
    """

    __tablename__ = "clinics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    place_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reviews_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    categories: Mapped[Optional[list[str]]] = mapped_column(
        JSONB, nullable=True, default=list
    )
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    opening_hours: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    additional_info: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    price_range: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    has_contract: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False
    )
    package_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        server_default=text("'{}'::uuid[]"),
        default=list,
    )

    packages: Mapped[List["Package"]] = relationship(
        "Package",
        secondary="clinic_packages",
        back_populates="clinics",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Clinic {self.id} ({self.title})>"
