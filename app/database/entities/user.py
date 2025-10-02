import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IdMixin

if typing.TYPE_CHECKING:
    from .connection import Connection


class User(Base, IdMixin):
    __tablename__ = "users"

    # Columns
    auth_id: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    connections: Mapped[list["Connection"]] = relationship("Connection", back_populates="user", default_factory=list, init=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("auth_id", name="uq_user_auth_id"),
        UniqueConstraint("phone_number", name="uq_user_phone_number"),
    )

    def __repr__(self):
        return f"<User {self.id}>"
