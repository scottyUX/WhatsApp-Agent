from typing import Annotated
from fastapi import Depends

from app.database.repositories import (
    UserRepository,
    ConnectionRepository,
    ConversationRepository,
    MessageRepository,
    MediaRepository,
    ConnectionChangeRepository,
)
from app.database.db import get_db


def get_user_repository(db: Annotated[object, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_message_repository(db: Annotated[object, Depends(get_db)]) -> MessageRepository:
    return MessageRepository(db)


def get_media_repository(db: Annotated[object, Depends(get_db)]) -> MediaRepository:
    return MediaRepository(db)


def get_connection_repository(db: Annotated[object, Depends(get_db)]) -> ConnectionRepository:
    return ConnectionRepository(db)


def get_conversation_repository(db: Annotated[object, Depends(get_db)]) -> ConversationRepository:
    return ConversationRepository(db)


def get_connection_change_repository(db: Annotated[object, Depends(get_db)]) -> ConnectionChangeRepository:
    return ConnectionChangeRepository(db)


# Repository dependencies
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
MediaRepositoryDep = Annotated[MediaRepository, Depends(get_media_repository)]
ConnectionRepositoryDep = Annotated[ConnectionRepository, Depends(get_connection_repository)]
ConversationRepositoryDep = Annotated[ConversationRepository, Depends(get_conversation_repository)]
ConnectionChangeRepositoryDep = Annotated[ConnectionChangeRepository, Depends(get_connection_change_repository)]