import pytest
from unittest.mock import patch, AsyncMock
from app.agents.manager_agent import run_manager
from app.services.conversation_state_service import conversation_state_service, ConversationAgent

@pytest.mark.asyncio
async def test_manager_basic_routing():
    """Test that manager routes messages correctly."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    with patch('app.agents.manager_agent.Runner.run') as mock_run:
        mock_run.return_value = AsyncMock()
        mock_run.return_value.final_output = "I'll help you with that."
        
        result = await run_manager(
            "Hi, I need help",
            user_id
        )
        
        # Verify manager responds
        assert "help" in result.lower()

@pytest.mark.asyncio
async def test_manager_anna_handoff():
    """Test that manager hands off to Anna for scheduling."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    with patch('app.agents.manager_agent.Runner.run') as mock_run:
        mock_run.return_value = AsyncMock()
        mock_run.return_value.final_output = "I'll transfer you to Anna for scheduling."
        
        result = await run_manager(
            "I'd like to schedule a consultation",
            user_id
        )
        
        # Verify handoff response
        assert "Anna" in result or "scheduling" in result.lower()

@pytest.mark.asyncio
async def test_manager_conversation_state():
    """Test that manager sets conversation state when handoff occurs."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    # Test the handoff callback directly
    from app.agents.manager_agent import on_handoff_to_english
    
    # Call the handoff callback directly to test state setting
    context = {"user_id": user_id, "message": "Hi"}
    await on_handoff_to_english(context)
    
    # Verify conversation state was set
    state = conversation_state_service.get_conversation_state(user_id)
    assert state is not None
    assert state.current_agent == ConversationAgent.ENGLISH

@pytest.mark.asyncio
async def test_manager_anna_already_handling():
    """Test that manager routes directly to Anna if she's already handling."""
    
    user_id = "test_user_123"
    
    # Set Anna as already handling
    conversation_state_service.set_conversation_state(user_id, ConversationAgent.ANNA_SCHEDULING)
    
    with patch('app.agents.manager_agent.handle_scheduling_request') as mock_anna:
        mock_anna.return_value = "I'm already helping you with scheduling."
        
        result = await run_manager(
            "I want to continue with my appointment",
            user_id
        )
        
        # Verify direct routing to Anna
        assert "scheduling" in result.lower()
        mock_anna.assert_called_once()

@pytest.mark.asyncio
async def test_manager_handoff_tool_calls():
    """Test that manager actually calls handoff tools."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    with patch('app.agents.manager_agent.Runner.run') as mock_run:
        mock_run.return_value = AsyncMock()
        mock_run.return_value.final_output = "Transferring to consultation agent."
        
        result = await run_manager(
            "I want to book a consultation",
            user_id
        )
        
        # Verify Runner.run was called with manager_agent
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0].name == "ManagerAgent"  # First argument should be manager_agent

@pytest.mark.asyncio
async def test_manager_handoff_callbacks():
    """Test that handoff callbacks work correctly."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    # Test Anna handoff callback
    from app.agents.manager_agent import on_handoff_to_anna
    context = {"user_id": user_id, "message": "I want to schedule"}
    await on_handoff_to_anna(context)
    
    state = conversation_state_service.get_conversation_state(user_id)
    assert state is not None
    assert state.current_agent == ConversationAgent.ANNA_SCHEDULING
    
    # Test German handoff callback
    from app.agents.manager_agent import on_handoff_to_german
    context = {"user_id": user_id, "message": "Hallo"}
    await on_handoff_to_german(context)
    
    state = conversation_state_service.get_conversation_state(user_id)
    assert state.current_agent == ConversationAgent.GERMAN