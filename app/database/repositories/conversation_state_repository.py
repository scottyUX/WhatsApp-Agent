import uuid
from typing import Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.entities import ConversationState
from app.models.enums import SchedulingStep


class ConversationStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        patient_profile_id: Union[str, uuid.UUID], 
        current_step: SchedulingStep,
    ) -> ConversationState:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        conversation_state = ConversationState(
            patient_profile_id=patient_profile_id,
            current_step=current_step,
        )
        self.db.add(conversation_state)
        self.db.commit()
        self.db.refresh(conversation_state)
        return conversation_state

    def save(self, conversation_state: ConversationState) -> ConversationState:
        self.db.add(conversation_state)
        self.db.commit()
        self.db.refresh(conversation_state)
        return conversation_state

    def get_by_id(self, conversation_state_id: Union[str, uuid.UUID]) -> Optional[ConversationState]:
        if isinstance(conversation_state_id, str):
            conversation_state_id = uuid.UUID(conversation_state_id)

        return self.db.query(ConversationState).filter(ConversationState.id == conversation_state_id).first()

    def get_latest_by_patient_profile_id(self, patient_profile_id: Union[str, uuid.UUID]) -> Optional[ConversationState]:
        """Get the most recent conversation state for a patient."""
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        return self.db.query(ConversationState).filter(
            ConversationState.patient_profile_id == patient_profile_id,
            ConversationState.deleted == False
        ).order_by(desc(ConversationState.last_activity)).first()
