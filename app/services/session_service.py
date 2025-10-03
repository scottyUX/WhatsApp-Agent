"""
Session Service for Persistent Conversation State Management

This service provides persistent session management for conversation state
in serverless environments by using the PostgreSQL database instead of
in-memory storage.

Key Features:
- Device ID based session tracking
- Persistent across serverless restarts
- TTL-based session expiration
- Integration with existing conversation_states table
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Union
from sqlalchemy.orm import Session

from app.database.entities import ConversationState, Connection
from app.database.repositories.conversation_state_repository import ConversationStateRepository
from app.database.repositories.connection_repository import ConnectionRepository
from app.models.enums import SchedulingStep


class SessionService:
    """Service for managing persistent conversation sessions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.conversation_state_repo = ConversationStateRepository(db)
        self.connection_repo = ConnectionRepository(db)
    
    def get_session_lock(self, device_id: str) -> Optional[str]:
        """
        Get the active agent for a device's conversation session.
        
        Args:
            device_id: The device identifier
            
        Returns:
            The active agent name if session is locked, None otherwise
        """
        try:
            # Convert device_id to deterministic UUID
            device_hash = hashlib.md5(device_id.encode()).hexdigest()
            device_uuid = uuid.UUID(device_hash[:32])
            
            conversation_state = self.db.query(ConversationState).filter(
                ConversationState.patient_profile_id == device_uuid,
                ConversationState.active_agent.isnot(None),
                ConversationState.locked_at.isnot(None)
            ).order_by(ConversationState.locked_at.desc()).first()
            
            if not conversation_state:
                return None
            
            # Check if session has expired
            if self._is_session_expired(conversation_state):
                self.clear_session_lock(device_id)
                return None
            
            return conversation_state.active_agent
            
        except Exception as e:
            print(f"Error getting session lock: {e}")
            return None
    
    def set_session_lock(self, device_id: str, agent_key: str) -> bool:
        """
        Set a session lock for a device to a specific agent.
        
        Args:
            device_id: The device identifier
            agent_key: The agent to lock to
            
        Returns:
            True if lock was set successfully, False otherwise
        """
        try:
            # Find or create conversation state
            conversation_state = self._get_or_create_conversation_state(device_id)
            
            # Update the conversation state with session lock
            conversation_state.active_agent = agent_key
            conversation_state.locked_at = datetime.now()
            conversation_state.last_activity = datetime.now()
            
            self.conversation_state_repo.save(conversation_state)
            return True
            
        except Exception as e:
            print(f"Error setting session lock: {e}")
            return False
    
    def clear_session_lock(self, device_id: str) -> bool:
        """
        Clear the session lock for a device.
        
        Args:
            device_id: The device identifier
            
        Returns:
            True if lock was cleared successfully, False otherwise
        """
        try:
            conversation_state = self._get_conversation_state_by_device(device_id)
            if conversation_state:
                conversation_state.active_agent = None
                conversation_state.locked_at = None
                conversation_state.last_activity = datetime.now()
                self.conversation_state_repo.save(conversation_state)
            return True
            
        except Exception as e:
            print(f"Error clearing session lock: {e}")
            return False
    
    def _is_session_expired(self, conversation_state: ConversationState) -> bool:
        """Check if a session has expired based on TTL."""
        if not conversation_state.locked_at:
            return True
        
        ttl_seconds = conversation_state.session_ttl or 86400  # Default 24 hours
        expiry_time = conversation_state.locked_at + timedelta(seconds=ttl_seconds)
        return datetime.now() > expiry_time
    
    def _get_or_create_conversation_state(self, device_id: str) -> ConversationState:
        """Get or create a conversation state for a device."""
        conversation_state = self._get_conversation_state_by_device(device_id)
        
        if not conversation_state:
            # Create a new conversation state
            # For chat users, we'll use a deterministic UUID based on device_id
            # This ensures the same device_id always gets the same UUID
            device_hash = hashlib.md5(device_id.encode()).hexdigest()
            device_uuid = uuid.UUID(device_hash[:32])
            
            conversation_state = ConversationState(
                patient_profile_id=device_uuid,
                current_step=SchedulingStep.INITIAL_CONTACT
            )
            self.db.add(conversation_state)
            self.db.commit()
            self.db.refresh(conversation_state)
        
        return conversation_state
    
    def _get_conversation_state_by_device(self, device_id: str) -> Optional[ConversationState]:
        """Get conversation state by device ID."""
        try:
            # Convert device_id to deterministic UUID
            device_hash = hashlib.md5(device_id.encode()).hexdigest()
            device_uuid = uuid.UUID(device_hash[:32])
            
            return self.db.query(ConversationState).filter(
                ConversationState.patient_profile_id == device_uuid
            ).order_by(ConversationState.locked_at.desc()).first()
        except Exception as e:
            print(f"Error getting conversation state: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            expired_sessions = self.db.query(ConversationState).filter(
                ConversationState.active_agent.isnot(None),
                ConversationState.locked_at.isnot(None)
            ).all()
            
            cleaned_count = 0
            for session in expired_sessions:
                if self._is_session_expired(session):
                    session.active_agent = None
                    session.locked_at = None
                    cleaned_count += 1
            
            if cleaned_count > 0:
                self.db.commit()
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up expired sessions: {e}")
            return 0
