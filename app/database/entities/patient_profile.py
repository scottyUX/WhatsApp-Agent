import typing
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import Gender
from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .medical_background import MedicalBackground
    from .conversation_state import ConversationState
    from .consultation import Consultation
    from .consultant_note import ConsultantNote
    from .patient_image_submission import PatientImageSubmission
    from .offer import Offer


class PatientProfile(Base, IdMixin):
    __tablename__ = "patient_profiles"

    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Required fields
    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)

    # Optional fields
    location: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[Optional[int]] = mapped_column(nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(nullable=True)
    # cal_booking_id: Mapped[Optional[str]] = mapped_column(nullable=True)  # TODO: Add after migration

    # Relationships
    conversation_states: Mapped[list["ConversationState"]] = relationship(
        "ConversationState",
        back_populates="patient_profile",
        init=False,
    )
    consultations: Mapped[list["Consultation"]] = relationship(
        "Consultation",
        back_populates="patient_profile",
        init=False,
    )
    consultant_notes: Mapped[list["ConsultantNote"]] = relationship(
        "ConsultantNote",
        back_populates="patient_profile",
        init=False,
    )
    medical_background: Mapped[Optional["MedicalBackground"]] = relationship(
        "MedicalBackground",
        back_populates="patient_profile",
        uselist=False,
        init=False
    )
    image_submissions: Mapped[list["PatientImageSubmission"]] = relationship(
        "PatientImageSubmission",
        back_populates="patient_profile",
        init=False
    )
    offers: Mapped[list["Offer"]] = relationship(
        "Offer",
        back_populates="patient_profile",
        init=False
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_patient_profile_user_id"),
    )

    def __repr__(self):
        return f"<PatientProfile {self.id} - {self.name}>"
