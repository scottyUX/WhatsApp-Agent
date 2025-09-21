"""
Pytest configuration and shared fixtures for WhatsApp Agent tests
"""
import os
import sys
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test environment setup
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('OPENAI_API_KEY', 'test-key')
os.environ.setdefault('TWILIO_ACCOUNT_SID', 'test-sid')
os.environ.setdefault('TWILIO_AUTH_TOKEN', 'test-token')
os.environ.setdefault('GOOGLE_PRIVATE_KEY', 'test-key')
os.environ.setdefault('GOOGLE_CLIENT_EMAIL', 'test@example.com')

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test response from OpenAI",
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "total_tokens": 100,
            "prompt_tokens": 50,
            "completion_tokens": 50
        }
    }

@pytest.fixture
def mock_twilio_message():
    """Mock Twilio message data"""
    return {
        "From": "whatsapp:+1234567890",
        "Body": "Test message",
        "MessageSid": "test-message-sid",
        "To": "whatsapp:+14155238886",
        "ProfileName": "Test User"
    }

@pytest.fixture
def sample_patient_profile():
    """Sample patient profile for testing"""
    from app.agents.specialized_agents.scheduling_models import PatientProfile, QuestionnaireStep
    
    return PatientProfile(
        name="John Doe",
        phone="+1234567890",
        email="john@example.com",
        questionnaire_step=QuestionnaireStep.NOT_STARTED
    )

@pytest.fixture
def sample_conversation_state():
    """Sample conversation state for testing"""
    from app.agents.specialized_agents.scheduling_models import ConversationState, SchedulingStep
    
    return ConversationState(
        user_id="test_user_123",
        current_step=SchedulingStep.INITIAL_CONTACT,
        phone_number="+1234567890",
        created_at=datetime.now(),
        last_activity=datetime.now()
    )

@pytest.fixture
def mock_calendar_service():
    """Mock Google Calendar service"""
    mock_service = Mock()
    mock_event = {
        'id': 'test-event-id',
        'htmlLink': 'https://calendar.google.com/event/test',
        'summary': 'Test Appointment'
    }
    mock_service.events().insert().execute.return_value = mock_event
    return mock_service

@pytest.fixture
def mock_questionnaire_manager():
    """Mock questionnaire manager"""
    from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
    
    manager = QuestionnaireManager()
    # Mock the database save method
    manager.save_responses_to_database = Mock()
    return manager

@pytest.fixture
def test_app():
    """FastAPI test client"""
    from app.app import app
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def mock_environment():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key',
        'TWILIO_ACCOUNT_SID': 'test-twilio-sid',
        'TWILIO_AUTH_TOKEN': 'test-twilio-token',
        'GOOGLE_PRIVATE_KEY': 'test-google-key',
        'GOOGLE_CLIENT_EMAIL': 'test@example.com',
        'GOOGLE_PROJECT_ID': 'test-project',
        'GOOGLE_CALENDAR_ID': 'test@example.com',
        'TESTING': 'true'
    }):
        yield

# Test data fixtures
@pytest.fixture
def sample_questions():
    """Sample questionnaire questions for testing"""
    from app.agents.specialized_agents.questionnaire_questions import Question
    
    return [
        Question(
            id="basic_country",
            text="What's your country?",
            category="basic_info",
            required=False
        ),
        Question(
            id="basic_age",
            text="What's your age?",
            category="basic_info",
            required=False
        )
    ]

@pytest.fixture
def sample_webhook_payload():
    """Sample webhook payload for testing"""
    return {
        "From": "whatsapp:+1234567890",
        "Body": "Hi, I'd like to schedule a consultation",
        "MessageSid": "test-message-sid",
        "To": "whatsapp:+14155238886",
        "ProfileName": "Test User",
        "NumMedia": "0"
    }

# Async test helpers
@pytest.fixture
def async_test():
    """Helper for async tests"""
    def _async_test(coro):
        return asyncio.get_event_loop().run_until_complete(coro)
    return _async_test

# Test markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "webhook: Webhook tests")
    config.addinivalue_line("markers", "agent: Agent tests")
    config.addinivalue_line("markers", "questionnaire: Questionnaire tests")
    config.addinivalue_line("markers", "calendar: Calendar tests")
    config.addinivalue_line("markers", "twilio: Twilio tests")