import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, connection_id: Union[str, uuid.UUID]) -> Conversation:
        # Convert string UUID to UUID object if needed
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        
        conversation = Conversation(connection_id=connection_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def save(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: Union[str, uuid.UUID]) -> Optional[Conversation]:
        if isinstance(conversation_id, str):
            conversation_id = uuid.UUID(conversation_id)
        
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_by_connection(self, connection_id: Union[str, uuid.UUID]) -> List[Conversation]:
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        
        return self.db.query(Conversation).filter(Conversation.connection_id == connection_id).order_by(Conversation.created_at.desc()).all()