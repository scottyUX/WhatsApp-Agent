"""
Example test template for developers
Copy this file and modify it for your new tests
"""
import pytest
from unittest.mock import Mock, patch
from app.agents.specialized_agents.scheduling_models import PatientProfile, QuestionnaireStep


@pytest.mark.unit
class TestExampleUnit:
    """Example unit test class - test individual components in isolation"""
    
    def test_example_function(self):
        """Test a simple function"""
        # Arrange
        input_value = "test input"
        expected_output = "expected output"
        
        # Act
        result = your_function(input_value)
        
        # Assert
        assert result == expected_output
    
    def test_example_with_fixture(self, sample_patient_profile):
        """Test using a shared fixture"""
        # The sample_patient_profile fixture is available from conftest.py
        assert sample_patient_profile.name == "John Doe"
        assert sample_patient_profile.questionnaire_step == QuestionnaireStep.NOT_STARTED


@pytest.mark.integration
class TestExampleIntegration:
    """Example integration test class - test component interactions"""
    
    def test_example_component_interaction(self, sample_conversation_state):
        """Test how two components work together"""
        from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
        
        # Arrange
        manager = QuestionnaireManager()
        
        # Act
        result = manager.start_questionnaire(sample_conversation_state)
        
        # Assert
        assert "questions" in result.lower()
        assert sample_conversation_state.patient_profile.questionnaire_step == QuestionnaireStep.BASIC_INFO


@pytest.mark.api
class TestExampleAPI:
    """Example API test class - test API endpoints"""
    
    def test_example_endpoint(self, test_app):
        """Test an API endpoint"""
        # Arrange
        test_data = {"key": "value"}
        
        # Act
        response = test_app.post("/api/example", json=test_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "success"


@pytest.mark.unit
class TestExampleWithMocks:
    """Example of using mocks for external dependencies"""
    
    @patch('app.services.openai_service.openai_client')
    def test_example_with_openai_mock(self, mock_openai_client, sample_conversation_state):
        """Test with OpenAI service mocked"""
        # Arrange
        mock_response = {
            "choices": [{"message": {"content": "Mocked response"}}]
        }
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Act
        from app.agents.manager_agent import run_manager
        result = run_manager("test message", sample_conversation_state)
        
        # Assert
        assert "Mocked response" in result
        mock_openai_client.chat.completions.create.assert_called_once()
    
    def test_example_with_custom_mock(self):
        """Test with a custom mock object"""
        # Arrange
        mock_service = Mock()
        mock_service.process.return_value = {"success": True, "data": "test"}
        
        # Act
        result = your_function_that_uses_service(mock_service)
        
        # Assert
        assert result["success"] is True
        mock_service.process.assert_called_once()


@pytest.mark.unit
class TestExampleDataValidation:
    """Example of testing data validation"""
    
    def test_valid_data(self):
        """Test with valid data"""
        from utils.validators import validate_email
        
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        assert error is None
    
    def test_invalid_data(self):
        """Test with invalid data"""
        from utils.validators import validate_email
        
        is_valid, error = validate_email("invalid-email")
        assert is_valid is False
        assert error is not None


# Example of parametrized tests
@pytest.mark.unit
@pytest.mark.parametrize("input_value,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("", False),
    ("test@", False),
])
def test_email_validation_parametrized(input_value, expected):
    """Test email validation with multiple inputs"""
    from utils.validators import validate_email
    
    is_valid, _ = validate_email(input_value)
    assert is_valid == expected


# Example of async tests
@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_function():
    """Test an async function"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = await your_async_function(input_data)
    
    # Assert
    assert result["status"] == "success"


# Example of test with setup and teardown
@pytest.mark.unit
class TestExampleWithSetup:
    """Example with setup and teardown"""
    
    def setup_method(self):
        """Run before each test method"""
        self.test_data = {"setup": "data"}
    
    def teardown_method(self):
        """Run after each test method"""
        # Clean up any resources
        pass
    
    def test_with_setup_data(self):
        """Test using setup data"""
        assert self.test_data["setup"] == "data"


# Example of test that should raise an exception
@pytest.mark.unit
def test_should_raise_exception():
    """Test that a function raises the expected exception"""
    with pytest.raises(ValueError, match="Invalid input"):
        your_function_that_should_raise_exception("invalid input")


# Example of test with custom markers
@pytest.mark.slow
@pytest.mark.unit
def test_slow_operation():
    """Test that takes a long time - marked as slow"""
    import time
    time.sleep(0.1)  # Simulate slow operation
    assert True


# Example of test with conditional skipping
@pytest.mark.unit
@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION_TESTS"), reason="Integration tests disabled")
def test_conditional_skip():
    """Test that only runs when environment variable is set"""
    assert True


# Example of test with custom fixture
@pytest.fixture
def custom_test_data():
    """Custom fixture for this test file"""
    return {"custom": "data", "for": "testing"}


@pytest.mark.unit
def test_with_custom_fixture(custom_test_data):
    """Test using a custom fixture"""
    assert custom_test_data["custom"] == "data"
