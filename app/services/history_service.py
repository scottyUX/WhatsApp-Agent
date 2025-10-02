from typing import List, Optional
import uuid

from app.database.entities.user import User
from app.database.entities.message import Message
from app.database.repositories import (
  UserRepository,
  MessageRepository,
  ConnectionRepository,
  ConversationRepository,
  ConnectionChangeRepository
)
from app.database.entities import Connection, Conversation


class HistoryService:
    def __init__(self, user_repository: UserRepository,
                 message_repository: MessageRepository,
                 connection_repository: ConnectionRepository,
                 conversation_repository: ConversationRepository,
                 connection_change_repository: ConnectionChangeRepository):
        self.user_repository = user_repository
        self.message_repository = message_repository
        self.connection_repository = connection_repository
        self.conversation_repository = conversation_repository
        self.connection_change_repository = connection_change_repository

    def get_or_create_user_by_phone_number(self, phone_number: str) -> User:
        """Get existing user by phone number or create a new one."""
        user = self.user_repository.get_by_phone_number(phone_number)
        if not user:
            user = self.user_repository.create(phone_number=phone_number)
        return user

## START - added from previous version -
    def get_or_create_connection(self,
                                 channel: str,
                                 device_id: Optional[str] = None,
                                 ip_address: Optional[str] = None,
                                 phone_number: Optional[str] = None
                                 ) -> Connection:
        """Get existing connection or create a new one."""
        if channel == "whatsapp":
            assert phone_number is not None
            user = self.get_or_create_user_by_phone_number(phone_number)
            whatsapp_connection = self.connection_repository.get_whatsapp_connection_by_user(user.id)
            if whatsapp_connection is not None:
                return whatsapp_connection
            else:
                return self.connection_repository.create(user_id=user.id, channel=channel)
        else:
            if device_id is not None:
                connection = self.connection_repository.get_by_device_id(device_id)
                if connection is not None:
                    return connection
            if ip_address is not None:
                connection = self.connection_repository.get_by_ip_address(ip_address)
                if connection is not None:
                    return connection
        # Create a new connection if none found
        user = self.user_repository.create()
        return self.connection_repository.create(user_id=user.id, channel=channel, device_id=device_id, ip_address=ip_address)


    def get_or_create_conversation(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> Conversation:
        """Get existing conversation or create a new one."""
        conversations = self.conversation_repository.get_by_connection(connection_id=connection_id)
        if conversations:
            # Return the most recent conversation (first one since they're ordered by created_at desc)
            return conversations[0]
        else:
            # Create a new conversation if none found
            return self.conversation_repository.create(connection_id=connection_id)


    def log_incoming_message_v1(self, conversation_id: uuid.UUID, content: Optional[str], media_url: Optional[str] = None) -> Message:
        """Log an incoming message from a user."""
        message = self.message_repository.create(
            conversation_id=conversation_id,
            sender="user",
            content=content,
        )
        if media_url:
            media_type = "image"
            self.media_repository.create(
                message_id=message.id,
                media_url=media_url,
                media_type=media_type
            )
        return message


    def log_outgoing_message_v1(self, conversation_id: uuid.UUID, content: str) -> Message:
        """Log an outgoing message to a user."""
        return self.message_repository.create(
            conversation_id=conversation_id,
            sender="agent",
            content=content
        )

    def get_message_history_v1(self, conversation_id: uuid.UUID, limit: int = 10) -> List[Message]:
        """Get recent message history for a conversation."""
        return self.message_repository.get_by_conversation(conversation_id=conversation_id, limit=limit)

## END - added from previous version -


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