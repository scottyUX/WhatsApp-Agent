import typing
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .connection import Connection
    from .message import Message


class Conversation(Base, IdMixin):
    __tablename__ = "conversations"

    # Columns
    connection_id: Mapped[UUID] = mapped_column(ForeignKey("connections.id"), nullable=False)

    # Relationships
    connection: Mapped["Connection"] = relationship("Connection", back_populates="conversations", init=False)
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", default_factory=list, init=False)

    def __repr__(self):
        return f"<Conversation {self.id}>"