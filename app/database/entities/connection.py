import typing
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import IdMixin
from .user import User

if typing.TYPE_CHECKING:
    from .conversation import Conversation


class Connection(Base, IdMixin):
    __tablename__ = "connections"

    # Columns
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String, nullable=True)
    channel = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="connections")
    conversations = relationship("Conversation", back_populates="connection")

    def __repr__(self):
        return f"<Connection {self.id}>"
