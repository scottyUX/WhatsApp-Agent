from typing import List, Optional
import uuid

from app.database.entities.user import User
from app.database.entities.message import Message
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.message_repository import MessageRepository


class HistoryService:
    def __init__(self, user_repository: UserRepository, message_repository: MessageRepository):
        self.user_repository = user_repository
        self.message_repository = message_repository

    def get_or_create_user(self, phone_number: str, name: Optional[str] = None) -> User:
        """Get existing user by phone number or create a new one."""
        user = self.user_repository.get_by_phone_number(phone_number)
        if not user:
            user = self.user_repository.create(phone_number=phone_number, name=name)
        return user

    def log_incoming_message(self, user_id: uuid.UUID, body: Optional[str], media_url: Optional[str] = None) -> Message:
        """Log an incoming message from a user."""
        return self.message_repository.create(
            user_id=user_id,
            direction="incoming",
            body=body,
            media_url=media_url
        )

    def log_outgoing_message(self, user_id: uuid.UUID, body: str) -> Message:
        """Log an outgoing message to a user."""
        return self.message_repository.create(
            user_id=user_id,
            direction="outgoing",
            body=body
        )

    def get_message_history(self, user_id: uuid.UUID, limit: int = 10) -> List[Message]:
        """Get recent message history for a user."""
        return self.message_repository.get_recent_by_user(user_id=user_id, limit=limit)

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        return self.user_repository.get_by_phone_number(phone_number)
    
    async def store_message(
        self, 
        phone_number: str, 
        content: str, 
        direction: str, 
        media_urls: List[str] = None
    ) -> Message:
        """Store a message (alias for compatibility with MessageService)."""
        user = self.get_or_create_user(phone_number)
        media_url = media_urls[0] if media_urls else None
        return self.log_incoming_message(user.id, content, media_url) if direction == "incoming" else self.log_outgoing_message(user.id, content)
    
    async def get_message_history_by_phone(self, phone_number: str, limit: int = 10) -> List[Message]:
        """Get message history by phone number (alias for compatibility)."""
        user = self.get_user_by_phone(phone_number)
        if not user:
            return []
        return self.get_message_history(user.id, limit)