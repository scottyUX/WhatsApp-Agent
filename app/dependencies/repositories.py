from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.patient_image_submission_repository import (
    PatientImageSubmissionRepository,
)
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.db import get_db


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_message_repository(db: Annotated[Session, Depends(get_db)]) -> MessageRepository:
    return MessageRepository(db)


def get_patient_image_submission_repository(
    db: Annotated[Session, Depends(get_db)]
) -> PatientImageSubmissionRepository:
    return PatientImageSubmissionRepository(db)


def get_patient_profile_repository(
    db: Annotated[Session, Depends(get_db)]
) -> PatientProfileRepository:
    return PatientProfileRepository(db)


# Repository dependencies
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
PatientImageSubmissionRepositoryDep = Annotated[
    PatientImageSubmissionRepository, Depends(get_patient_image_submission_repository)
]
PatientProfileRepositoryDep = Annotated[
    PatientProfileRepository, Depends(get_patient_profile_repository)
]
