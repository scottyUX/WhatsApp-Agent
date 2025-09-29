import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation_id: Union[str, uuid.UUID], sender: str, content: str) -> Message:
        # Convert string UUID to UUID object if needed
        if isinstance(conversation_id, str):
            conversation_id = uuid.UUID(conversation_id)
        
        msg = Message(conversation_id=conversation_id, sender=sender, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def save(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation(self, conversation_id: Union[str, uuid.UUID], limit: int = 10) -> List[Message]:
        # Convert string UUID to UUID object if needed
        if isinstance(conversation_id, str):
            conversation_id = uuid.UUID(conversation_id)

        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit).all()

    def get_by_id(self, message_id: Union[str, uuid.UUID]) -> Optional[Message]:
        # Convert string UUID to UUID object if needed
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        
        return self.db.query(Message).filter(Message.id == message_id).first()
