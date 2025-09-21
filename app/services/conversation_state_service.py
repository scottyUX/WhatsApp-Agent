"""
Conversation State Service for managing ongoing conversations.
Tracks which agent is currently handling a conversation to prevent context loss.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class ConversationAgent(Enum):
    """Types of agents that can handle conversations."""
    MANAGER = "manager"
    ANNA_SCHEDULING = "anna_scheduling"
    ENGLISH = "english"
    GERMAN = "german"
    SPANISH = "spanish"
    IMAGE = "image"

@dataclass
class ConversationState:
    """State of an ongoing conversation."""
    user_id: str
    current_agent: ConversationAgent
    started_at: datetime
    last_activity: datetime
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if the conversation has expired due to inactivity."""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

class ConversationStateService:
    """Service for managing conversation states."""
    
    def __init__(self):
        # In-memory storage for conversation states
        # In production, this should be stored in Redis or database
        self._conversations: Dict[str, ConversationState] = {}
    
    def get_conversation_state(self, user_id: str) -> Optional[ConversationState]:
        """Get the current conversation state for a user."""
        state = self._conversations.get(user_id)
        
        # Check if conversation has expired
        if state and state.is_expired():
            self._conversations.pop(user_id, None)
            return None
        
        return state
    
    def set_conversation_state(self, user_id: str, agent: ConversationAgent, context: Dict[str, Any] = None) -> ConversationState:
        """Set the conversation state for a user."""
        state = ConversationState(
            user_id=user_id,
            current_agent=agent,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            context=context or {}
        )
        self._conversations[user_id] = state
        return state
    
    def update_conversation_activity(self, user_id: str) -> bool:
        """Update the last activity for a conversation."""
        state = self._conversations.get(user_id)
        if state:
            state.update_activity()
            return True
        return False
    
    def clear_conversation_state(self, user_id: str) -> bool:
        """Clear the conversation state for a user."""
        if user_id in self._conversations:
            del self._conversations[user_id]
            return True
        return False
    
    def is_anna_handling_conversation(self, user_id: str) -> bool:
        """Check if Anna is currently handling a conversation."""
        state = self.get_conversation_state(user_id)
        return state is not None and state.current_agent == ConversationAgent.ANNA_SCHEDULING
    
    def get_anna_context(self, user_id: str) -> Dict[str, Any]:
        """Get Anna's context for a conversation."""
        state = self.get_conversation_state(user_id)
        if state and state.current_agent == ConversationAgent.ANNA_SCHEDULING:
            return state.context
        return {}

# Global instance
conversation_state_service = ConversationStateService()
