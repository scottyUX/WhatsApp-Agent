import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .conversation import Conversation
    from .media import Media


class Message(Base, IdMixin):
    __tablename__ = "messages"

    # Columns
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    sender: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages", init=False)
    media: Mapped[list["Media"]] = relationship("Media", back_populates="message", default_factory=list, init=False)

    def __repr__(self):
        return f"<Message {self.id}>"