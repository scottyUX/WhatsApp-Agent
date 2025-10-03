"""
Tests for Session Service

This module contains comprehensive tests for the persistent session management
functionality, including database operations, TTL handling, and error cases.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.session_service import SessionService
from app.database.entities import ConversationState, Connection
from app.models.enums import SchedulingStep


class TestSessionService:
    """Test cases for SessionService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def session_service(self, mock_db):
        """Create a SessionService instance with mocked database."""
        return SessionService(mock_db)
    
    @pytest.fixture
    def sample_device_id(self):
        """Sample device ID for testing."""
        return "test-device-123"
    
    @pytest.fixture
    def sample_conversation_state(self):
        """Sample conversation state for testing."""
        state = ConversationState()
        state.id = uuid.uuid4()
        state.patient_profile_id = uuid.uuid4()
        state.current_step = SchedulingStep.INITIAL_CONTACT
        state.active_agent = "scheduling"
        state.locked_at = datetime.now()
        state.session_ttl = 86400
        return state
    
    def test_get_session_lock_success(self, session_service, sample_device_id, sample_conversation_state):
        """Test successful retrieval of session lock."""
        # Mock the database query to return a conversation state
        session_service.db.query.return_value.join.return_value.filter.return_value.order_by.return_value.first.return_value = sample_conversation_state
        
        result = session_service.get_session_lock(sample_device_id)
        
        assert result == "scheduling"
        session_service.db.query.assert_called_once()
    
    def test_get_session_lock_not_found(self, session_service, sample_device_id):
        """Test retrieval of session lock when no conversation state exists."""
        # Mock the database query to return None
        session_service.db.query.return_value.join.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        result = session_service.get_session_lock(sample_device_id)
        
        assert result is None
    
    def test_get_session_lock_expired(self, session_service, sample_device_id):
        """Test retrieval of session lock when session has expired."""
        # Create an expired conversation state
        expired_state = ConversationState()
        expired_state.id = uuid.uuid4()
        expired_state.patient_profile_id = uuid.uuid4()
        expired_state.current_step = SchedulingStep.INITIAL_CONTACT
        expired_state.active_agent = "scheduling"
        expired_state.locked_at = datetime.now() - timedelta(hours=25)  # Expired
        expired_state.session_ttl = 86400  # 24 hours
        
        session_service.db.query.return_value.join.return_value.filter.return_value.order_by.return_value.first.return_value = expired_state
        
        result = session_service.get_session_lock(sample_device_id)
        
        assert result is None
        # Verify that clear_session_lock was called
        session_service.clear_session_lock.assert_called_once_with(sample_device_id)
    
    def test_set_session_lock_success(self, session_service, sample_device_id):
        """Test successful setting of session lock."""
        # Mock connection repository
        mock_connection = Connection()
        mock_connection.id = uuid.uuid4()
        session_service.connection_repo.get_by_device_id.return_value = mock_connection
        
        # Mock conversation state repository
        mock_conversation_state = ConversationState()
        mock_conversation_state.id = uuid.uuid4()
        session_service.conversation_state_repo.save.return_value = mock_conversation_state
        
        # Mock the _get_or_create_conversation_state method
        with patch.object(session_service, '_get_or_create_conversation_state', return_value=mock_conversation_state):
            result = session_service.set_session_lock(sample_device_id, "scheduling")
        
        assert result is True
        assert mock_conversation_state.active_agent == "scheduling"
        assert mock_conversation_state.locked_at is not None
        session_service.conversation_state_repo.save.assert_called_once_with(mock_conversation_state)
    
    def test_set_session_lock_create_connection(self, session_service, sample_device_id):
        """Test setting session lock when connection doesn't exist."""
        # Mock connection repository to return None (no existing connection)
        session_service.connection_repo.get_by_device_id.return_value = None
        session_service.connection_repo.create.return_value = Connection()
        
        # Mock conversation state repository
        mock_conversation_state = ConversationState()
        mock_conversation_state.id = uuid.uuid4()
        session_service.conversation_state_repo.save.return_value = mock_conversation_state
        
        # Mock the _get_or_create_conversation_state method
        with patch.object(session_service, '_get_or_create_conversation_state', return_value=mock_conversation_state):
            result = session_service.set_session_lock(sample_device_id, "scheduling")
        
        assert result is True
        session_service.connection_repo.create.assert_called_once()
    
    def test_clear_session_lock_success(self, session_service, sample_device_id, sample_conversation_state):
        """Test successful clearing of session lock."""
        # Mock the _get_conversation_state_by_device method
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=sample_conversation_state):
            result = session_service.clear_session_lock(sample_device_id)
        
        assert result is True
        assert sample_conversation_state.active_agent is None
        assert sample_conversation_state.locked_at is None
        session_service.conversation_state_repo.save.assert_called_once_with(sample_conversation_state)
    
    def test_clear_session_lock_not_found(self, session_service, sample_device_id):
        """Test clearing session lock when conversation state doesn't exist."""
        # Mock the _get_conversation_state_by_device method to return None
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=None):
            result = session_service.clear_session_lock(sample_device_id)
        
        assert result is True
        session_service.conversation_state_repo.save.assert_not_called()
    
    def test_is_session_expired_true(self, session_service):
        """Test session expiration check when session is expired."""
        expired_state = ConversationState()
        expired_state.locked_at = datetime.now() - timedelta(hours=25)
        expired_state.session_ttl = 86400  # 24 hours
        
        result = session_service._is_session_expired(expired_state)
        
        assert result is True
    
    def test_is_session_expired_false(self, session_service):
        """Test session expiration check when session is not expired."""
        active_state = ConversationState()
        active_state.locked_at = datetime.now() - timedelta(hours=1)
        active_state.session_ttl = 86400  # 24 hours
        
        result = session_service._is_session_expired(active_state)
        
        assert result is False
    
    def test_is_session_expired_no_locked_at(self, session_service):
        """Test session expiration check when locked_at is None."""
        state = ConversationState()
        state.locked_at = None
        
        result = session_service._is_session_expired(state)
        
        assert result is True
    
    def test_cleanup_expired_sessions(self, session_service):
        """Test cleanup of expired sessions."""
        # Create mock expired sessions
        expired_state1 = ConversationState()
        expired_state1.id = uuid.uuid4()
        expired_state1.active_agent = "scheduling"
        expired_state1.locked_at = datetime.now() - timedelta(hours=25)
        expired_state1.session_ttl = 86400
        
        expired_state2 = ConversationState()
        expired_state2.id = uuid.uuid4()
        expired_state2.active_agent = "image"
        expired_state2.locked_at = datetime.now() - timedelta(hours=30)
        expired_state2.session_ttl = 86400
        
        # Mock the database query
        session_service.db.query.return_value.filter.return_value.all.return_value = [expired_state1, expired_state2]
        
        result = session_service.cleanup_expired_sessions()
        
        assert result == 2
        assert expired_state1.active_agent is None
        assert expired_state1.locked_at is None
        assert expired_state2.active_agent is None
        assert expired_state2.locked_at is None
        session_service.db.commit.assert_called_once()
    
    def test_cleanup_expired_sessions_no_expired(self, session_service):
        """Test cleanup when no sessions are expired."""
        # Create mock active sessions
        active_state = ConversationState()
        active_state.id = uuid.uuid4()
        active_state.active_agent = "scheduling"
        active_state.locked_at = datetime.now() - timedelta(hours=1)
        active_state.session_ttl = 86400
        
        # Mock the database query
        session_service.db.query.return_value.filter.return_value.all.return_value = [active_state]
        
        result = session_service.cleanup_expired_sessions()
        
        assert result == 0
        assert active_state.active_agent == "scheduling"  # Should not be cleared
        session_service.db.commit.assert_not_called()
    
    def test_error_handling_get_session_lock(self, session_service, sample_device_id):
        """Test error handling in get_session_lock."""
        # Mock database to raise an exception
        session_service.db.query.side_effect = Exception("Database error")
        
        result = session_service.get_session_lock(sample_device_id)
        
        assert result is None
    
    def test_error_handling_set_session_lock(self, session_service, sample_device_id):
        """Test error handling in set_session_lock."""
        # Mock database to raise an exception
        session_service.connection_repo.get_by_device_id.side_effect = Exception("Database error")
        
        result = session_service.set_session_lock(sample_device_id, "scheduling")
        
        assert result is False
    
    def test_error_handling_clear_session_lock(self, session_service, sample_device_id):
        """Test error handling in clear_session_lock."""
        # Mock database to raise an exception
        session_service._get_conversation_state_by_device.side_effect = Exception("Database error")
        
        result = session_service.clear_session_lock(sample_device_id)
        
        assert result is False


class TestSessionServiceIntegration:
    """Integration tests for SessionService with real database operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a real database session for integration tests."""
        from app.database.db import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def session_service(self, db_session):
        """Create a SessionService instance with real database."""
        return SessionService(db_session)
    
    def test_full_session_lifecycle(self, session_service):
        """Test complete session lifecycle: set, get, clear."""
        device_id = f"test-device-{uuid.uuid4()}"
        
        # Test setting session lock
        result = session_service.set_session_lock(device_id, "scheduling")
        assert result is True
        
        # Test getting session lock
        active_agent = session_service.get_session_lock(device_id)
        assert active_agent == "scheduling"
        
        # Test clearing session lock
        result = session_service.clear_session_lock(device_id)
        assert result is True
        
        # Test that session lock is cleared
        active_agent = session_service.get_session_lock(device_id)
        assert active_agent is None
