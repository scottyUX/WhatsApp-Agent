import pytest
from unittest.mock import patch, AsyncMock
from app.agents.manager_agent import run_manager
from app.agents.specialized_agents.scheduling_agent_2 import handle_scheduling_request
from app.services.conversation_state_service import conversation_state_service, ConversationAgent

@pytest.mark.asyncio
async def test_manager_to_anna_flow():
    """Test complete flow from manager to Anna."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    # Test manager routing
    with patch('app.agents.manager_agent.Runner.run') as mock_run:
        mock_run.return_value = AsyncMock()
        mock_run.return_value.final_output = "I'll transfer you to Anna."
        
        result1 = await run_manager(
            "I'd like to schedule a consultation",
            user_id
        )
        
        # Verify manager response
        assert "Anna" in result1
    
    # Test Anna response
    with patch('app.agents.specialized_agents.scheduling_agent_2.Runner.run') as mock_run:
        mock_run.return_value = AsyncMock()
        mock_run.return_value.final_output = "Hello! I'm Anna, your consultation assistant."
        
        result2 = await handle_scheduling_request(
            "Hi",
            user_id
        )
        
        # Verify Anna response
        assert "Anna" in result2
        assert "consultation" in result2.lower()

@pytest.mark.asyncio
async def test_conversation_state_persistence():
    """Test that conversation state persists across calls."""
    
    user_id = "test_user_123"
    
    # Clear any existing state
    conversation_state_service.clear_conversation_state(user_id)
    
    # Set Anna as handling the conversation
    conversation_state_service.set_conversation_state(
        user_id,
        ConversationAgent.ANNA_SCHEDULING
    )
    
    # Verify Anna is handling the conversation
    assert conversation_state_service.is_anna_handling_conversation(user_id)
    
    # Clear the state
    conversation_state_service.clear_conversation_state(user_id)
    
    # Verify Anna is no longer handling the conversation
    assert not conversation_state_service.is_anna_handling_conversation(user_id)