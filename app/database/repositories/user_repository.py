from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.database.entities import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, auth_id: Optional[str] = None, name: Optional[str] = None, email: Optional[str] = None, phone_number: Optional[str] = None) -> User:
        user = User(auth_id=auth_id, name=name, email=email, phone_number=phone_number)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_auth_id(self, auth_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.auth_id == auth_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone_number).first()
