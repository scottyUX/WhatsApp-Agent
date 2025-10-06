"""
Tests for Session Service

This module contains comprehensive tests for the persistent session management
functionality, including database operations, TTL handling, and error cases.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.session_service import SessionService
from app.database.entities import ConversationState, Connection
from app.database.repositories.conversation_state_repository import ConversationStateRepository
from app.database.repositories.connection_repository import ConnectionRepository
from app.models.enums import SchedulingStep


def make_conversation_state(
    *,
    patient_profile_id: uuid.UUID | None = None,
    device_id: str | None = "test-device",
    current_step: SchedulingStep | str = SchedulingStep.INITIAL_CONTACT,
    active_agent: str | None = None,
    locked_at: datetime | None = None,
    session_ttl: int = 86400,
    openai_conversation_id: str | None = None,
):
    if isinstance(current_step, SchedulingStep):
        current_step_value = current_step.value
    else:
        current_step_value = current_step

    return ConversationState(
        patient_profile_id=patient_profile_id or uuid.uuid4(),
        device_id=device_id,
        current_step=current_step_value,
        active_agent=active_agent,
        locked_at=locked_at,
        session_ttl=session_ttl,
        openai_conversation_id=openai_conversation_id,
    )


class TestSessionService:
    """Test cases for SessionService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def session_service(self, mock_db):
        """Create a SessionService instance with mocked database."""
        service = SessionService(mock_db)
        service.conversation_state_repo = Mock(spec=ConversationStateRepository)
        service.connection_repo = Mock(spec=ConnectionRepository)
        return service
    
    @pytest.fixture
    def sample_device_id(self):
        """Sample device ID for testing."""
        return "test-device-123"
    
    @pytest.fixture
    def sample_conversation_state(self):
        """Sample conversation state for testing."""
        return make_conversation_state(
            active_agent="scheduling",
            locked_at=datetime.now(),
            openai_conversation_id="conv_123",
        )
    
    def test_get_session_lock_success(self, session_service, sample_device_id, sample_conversation_state):
        """Test successful retrieval of session lock."""
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=sample_conversation_state):
            result = session_service.get_session_lock(sample_device_id)

        assert result == "scheduling"

    def test_get_session_lock_not_found(self, session_service, sample_device_id):
        """Test retrieval of session lock when no conversation state exists."""
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=None):
            result = session_service.get_session_lock(sample_device_id)

        assert result is None

    def test_get_session_lock_expired(self, session_service, sample_device_id):
        """Test retrieval of session lock when session has expired."""
        # Create an expired conversation state
        expired_state = make_conversation_state(
            active_agent="scheduling",
            locked_at=datetime.now() - timedelta(hours=25),
            session_ttl=86400,
        )
        
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=expired_state):
            session_service.clear_session_lock = Mock(return_value=True)
            result = session_service.get_session_lock(sample_device_id)

        assert result is None
        # Verify that clear_session_lock was called
        session_service.clear_session_lock.assert_called_once_with(sample_device_id)
    
    def test_set_session_lock_success(self, session_service, sample_device_id):
        """Test successful setting of session lock."""
        # Mock connection repository
        mock_connection = Connection(
            user_id=uuid.uuid4(),
            device_id=None,
            ip_address=None,
            channel="chat",
        )
        mock_connection.id = uuid.uuid4()
        session_service.connection_repo.get_by_device_id.return_value = mock_connection
        
        # Mock conversation state repository
        mock_conversation_state = make_conversation_state()
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

        # Mock conversation state repository
        mock_conversation_state = make_conversation_state()
        session_service.conversation_state_repo.save.return_value = mock_conversation_state
        
        # Mock the _get_or_create_conversation_state method
        with patch.object(session_service, '_get_or_create_conversation_state', return_value=mock_conversation_state):
            result = session_service.set_session_lock(sample_device_id, "scheduling")

        assert result is True
        session_service.conversation_state_repo.save.assert_called_once_with(mock_conversation_state)
    
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
        expired_state = make_conversation_state(
            locked_at=datetime.now() - timedelta(hours=25),
            session_ttl=86400,
        )

        result = session_service._is_session_expired(expired_state)
        
        assert result is True
    
    def test_is_session_expired_false(self, session_service):
        """Test session expiration check when session is not expired."""
        active_state = make_conversation_state(
            locked_at=datetime.now() - timedelta(hours=1),
            session_ttl=86400,
        )
        
        result = session_service._is_session_expired(active_state)
        
        assert result is False
    
    def test_is_session_expired_no_locked_at(self, session_service):
        """Test session expiration check when locked_at is None."""
        state = make_conversation_state(locked_at=None)
        
        result = session_service._is_session_expired(state)
        
        assert result is True
    
    def test_cleanup_expired_sessions(self, session_service):
        """Test cleanup of expired sessions."""
        # Create mock expired sessions
        expired_state1 = make_conversation_state(
            active_agent="scheduling",
            locked_at=datetime.now() - timedelta(hours=25),
            session_ttl=86400,
            openai_conversation_id="conv_1",
        )
        
        expired_state2 = make_conversation_state(
            active_agent="image",
            locked_at=datetime.now() - timedelta(hours=30),
            session_ttl=86400,
            openai_conversation_id="conv_2",
        )
        
        # Mock the database query
        session_service.db.query.return_value.filter.return_value.all.return_value = [expired_state1, expired_state2]
        
        result = session_service.cleanup_expired_sessions()
        
        assert result == 2
        assert expired_state1.active_agent is None
        assert expired_state1.locked_at is None
        assert expired_state1.openai_conversation_id is None
        assert expired_state2.active_agent is None
        assert expired_state2.locked_at is None
        assert expired_state2.openai_conversation_id is None
        session_service.db.commit.assert_called_once()

    def test_get_openai_conversation_id(self, session_service, sample_device_id, sample_conversation_state):
        """Should return stored OpenAI conversation id."""
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=sample_conversation_state):
            result = session_service.get_openai_conversation_id(sample_device_id)

        assert result == "conv_123"

    def test_get_openai_conversation_id_missing(self, session_service, sample_device_id):
        """Should handle missing conversation state gracefully."""
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=None):
            result = session_service.get_openai_conversation_id(sample_device_id)

        assert result is None

    def test_set_openai_conversation_id(self, session_service, sample_device_id, sample_conversation_state):
        """Should persist conversation id and update timestamp."""
        with patch.object(session_service, '_get_or_create_conversation_state', return_value=sample_conversation_state):
            session_service.set_openai_conversation_id(sample_device_id, "conv_456")

        assert sample_conversation_state.openai_conversation_id == "conv_456"
        session_service.conversation_state_repo.save.assert_called_once_with(sample_conversation_state)

    def test_clear_openai_conversation_id(self, session_service, sample_device_id, sample_conversation_state):
        """Should clear stored conversation id."""
        with patch.object(session_service, '_get_conversation_state_by_device', return_value=sample_conversation_state):
            session_service.clear_openai_conversation_id(sample_device_id)

        assert sample_conversation_state.openai_conversation_id is None
        session_service.conversation_state_repo.save.assert_called_once_with(sample_conversation_state)
    
    def test_cleanup_expired_sessions_no_expired(self, session_service):
        """Test cleanup when no sessions are expired."""
        # Create mock active sessions
        active_state = make_conversation_state(
            active_agent="scheduling",
            locked_at=datetime.now() - timedelta(hours=1),
            session_ttl=86400,
        )
        
        # Mock the database query
        session_service.db.query.return_value.filter.return_value.all.return_value = [active_state]
        
        result = session_service.cleanup_expired_sessions()
        
        assert result == 0
        assert active_state.active_agent == "scheduling"  # Should not be cleared
        session_service.db.commit.assert_not_called()
    
    def test_error_handling_get_session_lock(self, session_service, sample_device_id):
        """Test error handling in get_session_lock."""
        # Mock database to raise an exception
        with patch.object(session_service, '_get_conversation_state_by_device', side_effect=Exception("Database error")):
            result = session_service.get_session_lock(sample_device_id)
        
        assert result is None
    
    def test_error_handling_set_session_lock(self, session_service, sample_device_id):
        """Test error handling in set_session_lock."""
        # Mock database to raise an exception
        with patch.object(session_service, '_get_or_create_conversation_state', side_effect=Exception("Database error")):
            result = session_service.set_session_lock(sample_device_id, "scheduling")
        
        assert result is False
    
    def test_error_handling_clear_session_lock(self, session_service, sample_device_id):
        """Test error handling in clear_session_lock."""
        # Mock database to raise an exception
        with patch.object(session_service, '_get_conversation_state_by_device', side_effect=Exception("Database error")):
            result = session_service.clear_session_lock(sample_device_id)
        
        assert result is False


class TestSessionServiceIntegration:
    """Integration tests for SessionService with real database operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a real database session for integration tests."""
        from app.database.db import SessionLocal
        db = SessionLocal()
        db.execute(text("""
            ALTER TABLE conversation_states
                ADD COLUMN IF NOT EXISTS device_id VARCHAR(255);
        """))
        db.execute(text("""
            ALTER TABLE conversation_states
                ADD COLUMN IF NOT EXISTS openai_conversation_id VARCHAR(255);
        """))
        db.execute(text("""
            ALTER TABLE conversation_states
                ALTER COLUMN patient_profile_id DROP NOT NULL;
        """))
        db.execute(text("""
            ALTER TABLE conversation_states
                ADD COLUMN IF NOT EXISTS active_agent VARCHAR(50);
        """))
        db.execute(text("""
            ALTER TABLE conversation_states
                ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE;
        """))
        db.execute(text("""
            ALTER TABLE conversation_states
                ADD COLUMN IF NOT EXISTS session_ttl INTEGER NOT NULL DEFAULT 86400;
        """))
        db.commit()
        try:
            yield db
        finally:
            try:
                db.execute(text("DELETE FROM conversation_states WHERE device_id LIKE 'test-device-%'"))
                db.commit()
            except Exception:
                db.rollback()
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
