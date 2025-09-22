import typing
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .user import User


class ConnectionChange(Base, IdMixin):
    __tablename__ = "connection_changes"

    # Columns
    from_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False) # merge or unmerge

    # Relationships
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id], back_populates="outgoing_connection_changes")
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id], back_populates="incoming_connection_changes")

    def __repr__(self):
        return f"<ConnectionChange {self.id}>"