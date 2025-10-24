import typing
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .patient_profile import PatientProfile


class PatientImageSubmission(Base, IdMixin):
    """Stores a bundle of patient images uploaded for analysis."""

    __tablename__ = "patient_image_submissions"

    patient_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patient_profiles.id"), nullable=False
    )
    image_urls: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    analysis_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    patient_profile: Mapped["PatientProfile"] = relationship(
        "PatientProfile", back_populates="image_submissions", init=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<PatientImageSubmission {self.id}>"
