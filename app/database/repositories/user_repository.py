from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.database.entities import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, phone_number: str, name: Optional[str] = None, email: Optional[str] = None) -> User:
        user = User(phone_number=phone_number, name=name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone_number).first()
