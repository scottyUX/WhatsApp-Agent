import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.enums import SchedulingStep
from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile


class ConversationState(Base, IdMixin):
    __tablename__ = "conversation_states"

    # Foreign key to patient profile (nullable for chat sessions)
    patient_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("patient_profiles.id"), nullable=True)

    # Device ID for chat sessions (alternative to patient_profile_id)
    device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Conversation state fields
    current_step: Mapped[SchedulingStep] = mapped_column(nullable=False)
    last_activity: Mapped[datetime] = mapped_column(server_default=func.now())
    
    # Session lock fields for conversation state management
    active_agent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    session_ttl: Mapped[int] = mapped_column(Integer, nullable=False, default=86400)  # 24 hours in seconds

    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile",
        back_populates="conversation_states",
        init=False
    )

    def __repr__(self):
        return f"<ConversationState {self.id} - {self.current_step}>"