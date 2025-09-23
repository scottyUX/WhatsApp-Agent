import uuid
from typing import List, Optional

from app.database.entities import User, Connection, Conversation, Message
from app.database.repositories import (
    UserRepository,
    ConnectionRepository,
    ConversationRepository,
    MessageRepository,
    MediaRepository,
)


class HistoryService:
    def __init__(self,
                 user_repository: UserRepository,
                 connection_repository: ConnectionRepository,
                 conversation_repository: ConversationRepository,
                 message_repository: MessageRepository,
                 media_repository: MediaRepository
                 ):
        self.user_repository = user_repository
        self.connection_repository = connection_repository
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.media_repository = media_repository


    def get_or_create_user_by_phone_number(self, phone_number: str) -> User:
        """Get existing user by phone number or create a new one."""
        user = self.user_repository.get_by_phone_number(phone_number)
        if not user:
            user = self.user_repository.create(phone_number=phone_number)
        return user


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


    def log_incoming_message(self, conversation_id: uuid.UUID, content: Optional[str], media_url: Optional[str] = None) -> Message:
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


    def log_outgoing_message(self, conversation_id: uuid.UUID, content: str) -> Message:
        """Log an outgoing message to a user."""
        return self.message_repository.create(
            conversation_id=conversation_id,
            sender="agent",
            content=content
        )


    def get_message_history(self, conversation_id: uuid.UUID, limit: int = 10) -> List[Message]:
        """Get recent message history for a conversation."""
        return self.message_repository.get_by_conversation(conversation_id=conversation_id, limit=limit)
