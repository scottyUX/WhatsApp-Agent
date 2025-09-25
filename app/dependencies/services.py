from typing import Annotated
from fastapi import Depends

from app.services.history_service import HistoryService
from app.services.message_service import MessageService
from app.dependencies.repositories import (
    get_user_repository,
    get_connection_repository,
    get_conversation_repository,
    get_message_repository,
    get_media_repository,
    get_connection_change_repository,
)


def get_history_service(
    user_repo: Annotated[object, Depends(get_user_repository)],
    connection_repo: Annotated[object, Depends(get_connection_repository)],
    conversation_repo: Annotated[object, Depends(get_conversation_repository)],
    message_repo: Annotated[object, Depends(get_message_repository)],
    media_repo: Annotated[object, Depends(get_media_repository)],
) -> HistoryService:
    return HistoryService(user_repo, connection_repo, conversation_repo, message_repo, media_repo)


def get_message_service(
    history_service: Annotated[HistoryService, Depends(get_history_service)]
) -> MessageService:
    return MessageService(history_service)


# Service dependencies
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
