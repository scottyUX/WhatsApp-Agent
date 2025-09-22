import typing
from uuid import UUID
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .connection import Connection
    from .message import Message


class Conversation(Base, IdMixin):
    __tablename__ = "conversations"

    # Columns
    connection_id: Mapped[UUID] = mapped_column(ForeignKey("connections.id"), nullable=False)

    # Relationships
    connection: Mapped["Connection"] = relationship("Connection", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation")

    def __repr__(self):
        return f"<Conversation {self.id}>"