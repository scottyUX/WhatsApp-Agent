"""
Tests for Manager Agent with Persistent Session Storage

This module contains tests for the updated manager agent that uses
persistent session storage instead of in-memory storage.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.agents.manager_agent import run_manager, _get_lock, _set_lock, _clear_lock


class TestManagerAgentPersistentSessions:
    """Test cases for manager agent with persistent sessions."""
    
    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        service = Mock()
        service.get_session_lock.return_value = None
        service.set_session_lock.return_value = True
        service.clear_session_lock.return_value = True
        return service
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return {
            "user_id": "test-device-123",
            "channel": "chat"
        }
    
    def test_get_lock_with_persistent_session(self, mock_session_service):
        """Test getting lock with persistent session service."""
        # Mock the session service to return an active agent
        mock_session_service.get_session_lock.return_value = "scheduling"
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            result = _get_lock("test-device-123")
        
        assert result == "scheduling"
        mock_session_service.get_session_lock.assert_called_once_with("test-device-123")
    
    def test_get_lock_no_active_session(self, mock_session_service):
        """Test getting lock when no active session exists."""
        # Mock the session service to return None
        mock_session_service.get_session_lock.return_value = None
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            result = _get_lock("test-device-123")
        
        assert result is None
        mock_session_service.get_session_lock.assert_called_once_with("test-device-123")
    
    def test_set_lock_with_persistent_session(self, mock_session_service):
        """Test setting lock with persistent session service."""
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            _set_lock("test-device-123", "scheduling")
        
        mock_session_service.set_session_lock.assert_called_once_with("test-device-123", "scheduling")
    
    def test_clear_lock_with_persistent_session(self, mock_session_service):
        """Test clearing lock with persistent session service."""
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            _clear_lock("test-device-123")
        
        mock_session_service.clear_session_lock.assert_called_once_with("test-device-123")
    
    def test_get_lock_database_error(self, mock_session_service):
        """Test error handling when getting lock fails."""
        # Mock the session service to raise an exception
        mock_session_service.get_session_lock.side_effect = Exception("Database error")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            result = _get_lock("test-device-123")
        
        assert result is None
    
    def test_set_lock_database_error(self, mock_session_service):
        """Test error handling when setting lock fails."""
        # Mock the session service to raise an exception
        mock_session_service.set_session_lock.side_effect = Exception("Database error")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            _set_lock("test-device-123", "scheduling")
        
        # Should not raise exception, just log error
        mock_session_service.set_session_lock.assert_called_once_with("test-device-123", "scheduling")
    
    def test_clear_lock_database_error(self, mock_session_service):
        """Test error handling when clearing lock fails."""
        # Mock the session service to raise an exception
        mock_session_service.clear_session_lock.side_effect = Exception("Database error")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            _clear_lock("test-device-123")
        
        # Should not raise exception, just log error
        mock_session_service.clear_session_lock.assert_called_once_with("test-device-123")
    
    @pytest.mark.asyncio
    async def test_run_manager_with_persistent_sessions(self, sample_context):
        """Test run_manager with persistent session storage."""
        # Mock the session service
        mock_session_service = Mock()
        mock_session_service.get_session_lock.return_value = None
        mock_session_service.set_session_lock.return_value = True
        mock_session_service.clear_session_lock.return_value = True
        
        # Mock the agent runner
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Test response")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service), \
             patch('app.agents.manager_agent.AGENTS', {"scheduling": mock_agent}), \
             patch('app.agents.manager_agent._detect_intent', return_value="scheduling"):
            
            result = await run_manager("I want to schedule an appointment", sample_context)
        
        # Verify session operations
        mock_session_service.get_session_lock.assert_called_once_with("test-device-123")
        mock_session_service.set_session_lock.assert_called_once_with("test-device-123", "scheduling")
        
        # Verify agent was called
        mock_agent.run.assert_called_once()
        
        # Verify result
        assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_run_manager_with_existing_session(self, sample_context):
        """Test run_manager when session already exists."""
        # Mock the session service to return an existing session
        mock_session_service = Mock()
        mock_session_service.get_session_lock.return_value = "scheduling"
        mock_session_service.clear_session_lock.return_value = True
        
        # Mock the agent runner
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Test response")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service), \
             patch('app.agents.manager_agent.AGENTS', {"scheduling": mock_agent}):
            
            result = await run_manager("I want to schedule an appointment", sample_context)
        
        # Verify session operations
        mock_session_service.get_session_lock.assert_called_once_with("test-device-123")
        mock_session_service.set_session_lock.assert_not_called()  # Should not set new lock
        
        # Verify agent was called
        mock_agent.run.assert_called_once()
        
        # Verify result
        assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_run_manager_reset_keywords(self, sample_context):
        """Test run_manager with reset keywords."""
        # Mock the session service
        mock_session_service = Mock()
        mock_session_service.get_session_lock.return_value = "scheduling"
        mock_session_service.clear_session_lock.return_value = True
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service):
            result = await run_manager("reset", sample_context)
        
        # Verify session was cleared
        mock_session_service.clear_session_lock.assert_called_once_with("test-device-123")
        
        # Verify reset response
        assert "I've reset our conversation" in result
    
    @pytest.mark.asyncio
    async def test_run_manager_session_expired(self, sample_context):
        """Test run_manager when session has expired."""
        # Mock the session service to return None (expired session)
        mock_session_service = Mock()
        mock_session_service.get_session_lock.return_value = None
        mock_session_service.set_session_lock.return_value = True
        
        # Mock the agent runner
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value="Test response")
        
        with patch('app.agents.manager_agent._get_session_service', return_value=mock_session_service), \
             patch('app.agents.manager_agent.AGENTS', {"scheduling": mock_agent}), \
             patch('app.agents.manager_agent._detect_intent', return_value="scheduling"):
            
            result = await run_manager("I want to schedule an appointment", sample_context)
        
        # Verify new session was created
        mock_session_service.set_session_lock.assert_called_once_with("test-device-123", "scheduling")
        
        # Verify agent was called
        mock_agent.run.assert_called_once()
        
        # Verify result
        assert result == "Test response"


class TestManagerAgentIntegration:
    """Integration tests for manager agent with persistent sessions."""
    
    @pytest.mark.asyncio
    async def test_conversation_persistence_across_requests(self):
        """Test that conversations persist across multiple requests."""
        device_id = "test-device-persistence"
        context = {"user_id": device_id, "channel": "chat"}
        
        # First request - should create new session
        with patch('app.agents.manager_agent._get_session_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_session_lock.return_value = None
            mock_service.set_session_lock.return_value = True
            mock_get_service.return_value = mock_service
            
            with patch('app.agents.manager_agent.AGENTS', {"scheduling": Mock()}):
                result1 = await run_manager("I want to schedule an appointment", context)
        
        # Second request - should use existing session
        with patch('app.agents.manager_agent._get_session_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_session_lock.return_value = "scheduling"  # Existing session
            mock_service.clear_session_lock.return_value = True
            mock_get_service.return_value = mock_service
            
            with patch('app.agents.manager_agent.AGENTS', {"scheduling": Mock()}):
                result2 = await run_manager("What are your available times?", context)
        
        # Verify that second request used existing session
        mock_service.set_session_lock.assert_not_called()  # Should not create new session
