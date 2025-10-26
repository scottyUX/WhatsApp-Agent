import logging
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.services.history_service import HistoryService
from app.services.message_service import MessageService
from app.services.patient_image_service import PatientImageService
from app.services.supabase_storage_service import SupabaseStorageService
from app.dependencies.repositories import (
    get_user_repository,
    get_message_repository,
    get_patient_image_submission_repository,
    get_patient_profile_repository,
)
from app.database.repositories.patient_image_submission_repository import (
    PatientImageSubmissionRepository,
)
from app.database.repositories.patient_profile_repository import (
    PatientProfileRepository,
)

logger = logging.getLogger(__name__)

def get_history_service(
    user_repo: Annotated[object, Depends(get_user_repository)],
    message_repo: Annotated[object, Depends(get_message_repository)]
) -> HistoryService:
    return HistoryService(user_repo, message_repo)


def get_message_service(
    history_service: Annotated[HistoryService, Depends(get_history_service)]
) -> MessageService:
    return MessageService(history_service)


@lru_cache(maxsize=1)
def _get_storage_service_cached() -> SupabaseStorageService:
    return SupabaseStorageService()


def get_supabase_storage_service() -> SupabaseStorageService:
    return _get_storage_service_cached()


def get_patient_image_service(
    repository: Annotated[
        PatientImageSubmissionRepository,
        Depends(get_patient_image_submission_repository),
    ],
    profile_repository: Annotated[
        PatientProfileRepository,
        Depends(get_patient_profile_repository),
    ],
) -> PatientImageService:
    try:
        storage_service: SupabaseStorageService | None = get_supabase_storage_service()
    except RuntimeError as exc:
        logger.warning("Supabase storage unavailable: %s", exc)
        storage_service = None

    return PatientImageService(repository, profile_repository, storage_service)


# Service dependencies
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
PatientImageServiceDep = Annotated[PatientImageService, Depends(get_patient_image_service)]
