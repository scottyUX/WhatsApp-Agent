import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import Message


class MessageRepository:
    def __init__(self, db: Session):
       self.db = db

    def create(self, user_id: Union[str, uuid.UUID], direction: str, body: Optional[str], media_url: Optional[str] = None) -> Message:
        # Convert string UUID to UUID object if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        msg = Message(user_id=user_id, direction=direction, body=body, media_url=media_url)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_by_user(self, user_id: Union[str, uuid.UUID]) -> List[Message]:
        # Convert string UUID to UUID object if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        return self.db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).all()

    def get_by_id(self, message_id: Union[str, uuid.UUID]) -> Optional[Message]:
        # Convert string UUID to UUID object if needed
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_recent_by_user(self, user_id: Union[str, uuid.UUID], limit: int = 10) -> List[Message]:
        # Convert string UUID to UUID object if needed
        if isinstance(user_id, str):
          user_id = uuid.UUID(user_id)
        
        return self.db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).limit(limit).all()
