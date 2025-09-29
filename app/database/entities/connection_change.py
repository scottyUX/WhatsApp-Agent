import typing
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    pass


class ConnectionChange(Base, IdMixin):
    __tablename__ = "connection_changes"

    # Columns
    from_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False) # merge or unmerge

    def __repr__(self):
        return f"<ConnectionChange {self.id}>"
