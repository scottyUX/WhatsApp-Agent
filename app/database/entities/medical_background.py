import typing
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile


class MedicalBackground(Base, IdMixin):
    __tablename__ = "medical_backgrounds"

    # Foreign key to patient profile
    patient_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patient_profiles.id"), nullable=False)

    # Medical data stored as JSONB
    # This will contain:
    # - chronic_illnesses: List[str]
    # - current_medications: List[str]
    # - allergies: List[str]
    # - surgeries: List[str]
    # - heart_conditions: List[str]
    # - contagious_diseases: List[str]
    # - hair_loss_locations: List[str]  # crown, hairline, top
    # - hair_loss_start: Optional[str]
    # - family_history: Optional[bool]
    # - previous_treatments: List[str]
    medical_data: Mapped[dict] = mapped_column(JSONB, default_factory=dict)

    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile",
        back_populates="medical_background",
        init=False
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("patient_profile_id", name="uq_medical_background_patient_profile_id"),
    )

    def __repr__(self):
        return f"<MedicalBackground {self.id} - Patient {self.patient_profile_id}>"