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
    
    def get_by_device_id(self, device_id: Union[str, uuid.UUID]) -> Optional[ConversationState]:
        """Get the latest conversation state for a device ID."""
        # Handle both UUID and string device IDs
        if isinstance(device_id, str):
            try:
                # Try to convert to UUID, but don't fail if it's not a valid UUID
                device_id = uuid.UUID(device_id)
            except ValueError:
                # Keep as string if it's not a valid UUID
                pass
        
        # This is a simplified lookup - in production you might want to join through connections
        return self.db.query(ConversationState).filter(
            ConversationState.device_id == device_id,
            ConversationState.deleted == False
        ).order_by(desc(ConversationState.last_activity)).first()
    
    def update_session_lock(self, conversation_state_id: Union[str, uuid.UUID], 
                          active_agent: Optional[str] = None, 
                          locked_at: Optional[datetime] = None) -> Optional[ConversationState]:
        """Update session lock fields for a conversation state."""
        if isinstance(conversation_state_id, str):
            conversation_state_id = uuid.UUID(conversation_state_id)
        
        conversation_state = self.get_by_id(conversation_state_id)
        if conversation_state:
            if active_agent is not None:
                conversation_state.active_agent = active_agent
            if locked_at is not None:
                conversation_state.locked_at = locked_at
            conversation_state.last_activity = datetime.now()
            return self.save(conversation_state)
        
        return None