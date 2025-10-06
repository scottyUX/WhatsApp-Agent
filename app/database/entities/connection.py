import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin
from .user import User

if typing.TYPE_CHECKING:
    from .conversation import Conversation


class Connection(Base, IdMixin):
    __tablename__ = "connections"

    # Columns
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    channel: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="connections", init=False)
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="connection", default_factory=list, init=False)

    def __repr__(self):
        return f"<Connection {self.id}>"
