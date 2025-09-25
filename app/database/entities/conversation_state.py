import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.enums import SchedulingStep
from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile


class ConversationState(Base, IdMixin):
    __tablename__ = "conversation_states"

    # Foreign key to patient profile
    patient_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patient_profiles.id"), nullable=False)

    # Conversation state fields
    current_step: Mapped[SchedulingStep] = mapped_column(nullable=False)
    last_activity: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile",
        back_populates="conversation_states",
        init=False
    )

    def __repr__(self):
        return f"<ConversationState {self.id} - {self.current_step}>"