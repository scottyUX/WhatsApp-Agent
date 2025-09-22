import typing
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class Connection(Base, IdMixin):
    __tablename__ = "connections"

    # Columns
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    device_id: Mapped[Optional[UUID]] = mapped_column(UUID, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    channel: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="connections")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="connection")

    def __repr__(self):
        return f"<Connection {self.id}>"