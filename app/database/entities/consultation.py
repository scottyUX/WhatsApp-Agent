import typing
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedAsDataclass
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import Base

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile
    from .consultant_note import ConsultantNote


class Consultation(Base, MappedAsDataclass):
    __tablename__ = "Appoinment"

    # Primary key and timestamps
    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    # Required fields first - mapped to actual column names
    zoom_meeting_id: Mapped[str] = mapped_column("zoomMeetingId", String, nullable=False)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    attendee_name: Mapped[str] = mapped_column("attendeeName", String, nullable=False)
    attendee_email: Mapped[str] = mapped_column("attendeeEmail", String, nullable=False)
    raw_payload: Mapped[dict] = mapped_column("rawPayload", JSONB, nullable=False)
    host_name: Mapped[str] = mapped_column("hostName", String, nullable=False)
    host_email: Mapped[str] = mapped_column("hostEmail", String, nullable=False)
    
    # Foreign key to patient profile (after required fields)
    patient_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "patient_profile_id",
        ForeignKey("patient_profiles.id"), 
        nullable=True,
        default=None
    )
    
    # Optional fields after required ones - mapped to actual column names
    host_id: Mapped[Optional[str]] = mapped_column("hostId", String, nullable=True, default=None)
    agenda: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    start_time: Mapped[Optional[datetime]] = mapped_column("startTime", DateTime, nullable=True, default=None)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    timezone: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    join_url: Mapped[Optional[str]] = mapped_column("joinUrl", String, nullable=True, default=None)
    start_url: Mapped[Optional[str]] = mapped_column("startUrl", String, nullable=True, default=None)
    attendee_phone: Mapped[Optional[str]] = mapped_column("attendeePhone", String, nullable=True, default=None)
    host_join_token: Mapped[Optional[str]] = mapped_column("hostJoinToken", String, nullable=True, default=None)
    participant_join_token: Mapped[Optional[str]] = mapped_column("participantJoinToken", String, nullable=True, default=None)
    join_token_expires_at: Mapped[Optional[datetime]] = mapped_column("joinTokenExpiresAt", DateTime, nullable=True, default=None)
    join_url_base: Mapped[Optional[str]] = mapped_column("joinUrlBase", String, nullable=True, default=None)
    
    # Relationships
    patient_profile: Mapped[Optional["PatientProfile"]] = relationship(
        "PatientProfile",
        back_populates="consultations"
    )
    consultant_notes: Mapped[list["ConsultantNote"]] = relationship(
        "ConsultantNote",
        back_populates="consultation",
        default_factory=list,
        init=False
    )

    def __repr__(self):
        return f"<Consultation {self.id} - {self.topic or 'Untitled'} ({self.start_time})>"
