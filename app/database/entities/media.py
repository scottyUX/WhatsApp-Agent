import typing
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.enums import MediaType
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .message import Message


class Media(Base, IdMixin):
    __tablename__ = "media"

    # Columns
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id"), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), nullable=False)
    media_url: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="media")

    def __repr__(self):
        return f"<Media {self.id}>"