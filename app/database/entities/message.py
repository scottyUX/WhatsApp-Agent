import typing
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

if typing.TYPE_CHECKING:
    from .media import Media

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    direction = Column(String, nullable=False)  # "incoming" | "outgoing"
    body = Column(String, nullable=True)
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("direction in ('incoming','outgoing')", name="direction_check"),
    )

    media = relationship("Media", back_populates="message", cascade="all, delete-orphan")
