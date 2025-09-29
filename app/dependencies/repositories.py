from typing import Annotated
from fastapi import Depends

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.message_repository import MessageRepository
from app.database.db import get_db


def get_user_repository(db: Annotated[object, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_message_repository(db: Annotated[object, Depends(get_db)]) -> MessageRepository:
    return MessageRepository(db)


# Repository dependencies
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
