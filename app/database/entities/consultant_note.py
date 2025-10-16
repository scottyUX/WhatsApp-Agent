import typing
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedAsDataclass
from sqlalchemy.sql import func

from .base import Base

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile
    from .consultation import Consultation


class ConsultantNote(Base, MappedAsDataclass):
    __tablename__ = "consultant_notes"

    # Primary key and timestamps
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    # Required fields
    patient_profile_id: Mapped[uuid.UUID] = mapped_column(
        "patient_profile_id",
        ForeignKey("patient_profiles.id"), 
        nullable=False
    )
    consultant_email: Mapped[str] = mapped_column("consultant_email", String, nullable=False)
    note_content: Mapped[str] = mapped_column("note_content", Text, nullable=False)
    
    # Optional fields
    consultation_id: Mapped[Optional[str]] = mapped_column(
        "consultation_id",
        ForeignKey("Appoinment.id"),
        nullable=True,
        default=None
    )
    note_type: Mapped[Optional[str]] = mapped_column("note_type", String, nullable=True, default="general")
    is_private: Mapped[bool] = mapped_column("is_private", nullable=False, default=False)
    
    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile",
        back_populates="consultant_notes"
    )
    consultation: Mapped[Optional["Consultation"]] = relationship(
        "Consultation",
        back_populates="consultant_notes"
    )

    def __repr__(self):
        return f"<ConsultantNote {self.id} - {self.note_content[:50]}...>"
