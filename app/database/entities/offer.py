import typing
import uuid
from typing import Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, text, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedAsDataclass

from .base import Base

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile
    from .patient_image_submission import PatientImageSubmission


class Offer(Base, MappedAsDataclass):
    __tablename__ = "offers"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")  # requires pgcrypto extension
    )

    # Core relationships
    patient_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Clinic selection (up to 3 clinics)
    clinic_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        server_default=text("'{}'::uuid[]"),
        default=list,
    )

    # Pricing snapshot
    total_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default="USD",
        default="USD",
    )
    deposit_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Payment options
    payment_methods: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default=text("'{}'::text[]"),
        default=list,
    )

    # Status lifecycle
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="draft",
        default="draft",
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        nullable=True,
    )

    # Status history (track all status changes)
    status_history: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        default=dict,
    )

    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        default=datetime.now,
    )

    # Relationships
    patient_profile: Mapped[Optional["PatientProfile"]] = relationship(
        "PatientProfile",
        back_populates="offers",
    )

    def __repr__(self):
        return f"<Offer {self.id} - {self.status} for patient {self.patient_profile_id}>"

    def add_status_history(self, status: str, notes: str = None, changed_by: uuid.UUID = None):
        """Add a status change entry to the history"""
        if not isinstance(self.status_history, list):
            self.status_history = []
        
        history_entry = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "changed_by": str(changed_by) if changed_by else None,
        }
        
        self.status_history.append(history_entry)
        self.status = status

