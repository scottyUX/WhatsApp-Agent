"""
End-to-end tests for complete system functionality
These tests simulate real user interactions and verify the entire system works
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.app import app


@pytest.mark.e2e
class TestCompleteUserJourney:
    """Test complete user journey from start to finish"""
    
    def test_complete_consultation_scheduling_journey(self, mock_environment):
        """Test complete consultation scheduling journey"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            with patch('app.agents.specialized_agents.scheduling_agent_2.openai_client') as mock_anna:
                with patch('app.tools.google_calendar_tools.get_calendar_service') as mock_calendar:
                    # Mock OpenAI responses for intent detection
                    mock_openai.chat.completions.create.return_value = Mock(
                        choices=[Mock(message=Mock(content="YES"))]
                    )
                    
                    # Mock Anna's responses
                    mock_anna.chat.completions.create.return_value = Mock(
                        choices=[Mock(message=Mock(content="Hello! I'm Anna. I'd be happy to help you schedule a consultation."))]
                    )
                    
                    # Mock calendar service
                    mock_calendar.return_value.events().insert().execute.return_value = {
                        'id': 'test-event-id',
                        'htmlLink': 'https://calendar.google.com/event/test'
                    }
                    
                    client = TestClient(app)
                    
                    # Step 1: Initial consultation request
                    response1 = client.post("/api/webhook", data={
                        "From": "whatsapp:+1234567890",
                        "Body": "Hi, I'd like to schedule a consultation",
                        "MessageSid": "test-1",
                        "To": "whatsapp:+14155238886"
                    })
                    assert response1.status_code == 200
                    assert "Response" in response1.text
                    
                    # Step 2: User agrees to provide information
                    response2 = client.post("/api/webhook", data={
                        "From": "whatsapp:+1234567890",
                        "Body": "yes",
                        "MessageSid": "test-2",
                        "To": "whatsapp:+14155238886"
                    })
                    assert response2.status_code == 200
                    assert "Response" in response2.text
                    
                    # Step 3: User provides contact information
                    response3 = client.post("/api/webhook", data={
                        "From": "whatsapp:+1234567890",
                        "Body": "John Doe +1234567890 john@example.com",
                        "MessageSid": "test-3",
                        "To": "whatsapp:+14155238886"
                    })
                    assert response3.status_code == 200
                    assert "Response" in response3.text
    
    def test_questionnaire_completion_journey(self, mock_environment):
        """Test complete questionnaire completion journey"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            with patch('app.agents.specialized_agents.scheduling_agent_2.openai_client') as mock_anna:
                # Mock OpenAI responses
                mock_openai.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="YES"))]
                )
                
                # Mock Anna's responses for questionnaire
                mock_anna.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="Let's start with some questions. What's your country?"))]
                )
                
                client = TestClient(app)
                
                # Start questionnaire
                response1 = client.post("/api/webhook", data={
                    "From": "whatsapp:+1234567890",
                    "Body": "yes",
                    "MessageSid": "test-1",
                    "To": "whatsapp:+14155238886"
                })
                assert response1.status_code == 200
                
                # Answer questionnaire questions
                questionnaire_answers = [
                    "United States",
                    "35",
                    "Male",
                    "Diabetes",
                    "Metformin",
                    "COVID-19 last month",
                    "2 years ago, gradually",
                    "Crown area",
                    "Minoxidil, didn't work"
                ]
                
                for i, answer in enumerate(questionnaire_answers):
                    response = client.post("/api/webhook", data={
                        "From": "whatsapp:+1234567890",
                        "Body": answer,
                        "MessageSid": f"test-{i+2}",
                        "To": "whatsapp:+14155238886"
                    })
                    assert response.status_code == 200
                    assert "Response" in response.text
    
    def test_questionnaire_skip_journey(self, mock_environment):
        """Test questionnaire skip journey"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            with patch('app.agents.specialized_agents.scheduling_agent_2.openai_client') as mock_anna:
                # Mock OpenAI responses
                mock_openai.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="YES"))]
                )
                
                # Mock Anna's responses
                mock_anna.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="Let's start with some questions. What's your country?"))]
                )
                
                client = TestClient(app)
                
                # Start questionnaire
                response1 = client.post("/api/webhook", data={
                    "From": "whatsapp:+1234567890",
                    "Body": "yes",
                    "MessageSid": "test-1",
                    "To": "whatsapp:+14155238886"
                })
                assert response1.status_code == 200
                
                # Skip all questions
                for i in range(9):  # 9 questions total
                    response = client.post("/api/webhook", data={
                        "From": "whatsapp:+1234567890",
                        "Body": "skip",
                        "MessageSid": f"test-{i+2}",
                        "To": "whatsapp:+14155238886"
                    })
                    assert response.status_code == 200
                    assert "Response" in response.text


@pytest.mark.e2e
class TestErrorHandling:
    """Test error handling in end-to-end scenarios"""
    
    def test_invalid_webhook_payload(self, mock_environment):
        """Test handling of invalid webhook payload"""
        client = TestClient(app)
        
        # Test with missing required fields
        response = client.post("/api/webhook", data={})
        assert response.status_code == 200
        assert "Response" in response.text
    
    def test_malformed_message_handling(self, mock_environment):
        """Test handling of malformed messages"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            mock_openai.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="NO"))]
            )
            
            client = TestClient(app)
            
            # Test with empty message
            response = client.post("/api/webhook", data={
                "From": "whatsapp:+1234567890",
                "Body": "",
                "MessageSid": "test-1",
                "To": "whatsapp:+14155238886"
            })
            assert response.status_code == 200
            assert "Response" in response.text
    
    def test_openai_api_failure_handling(self, mock_environment):
        """Test handling of OpenAI API failures"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            # Mock API failure
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
            
            client = TestClient(app)
            
            response = client.post("/api/webhook", data={
                "From": "whatsapp:+1234567890",
                "Body": "I'd like to schedule a consultation",
                "MessageSid": "test-1",
                "To": "whatsapp:+14155238886"
            })
            assert response.status_code == 200
            assert "Response" in response.text


@pytest.mark.e2e
class TestPerformance:
    """Test system performance under load"""
    
    def test_concurrent_requests(self, mock_environment):
        """Test handling of concurrent requests"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            with patch('app.agents.specialized_agents.scheduling_agent_2.openai_client') as mock_anna:
                # Mock responses
                mock_openai.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="YES"))]
                )
                mock_anna.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="Hello! I'm Anna."))]
                )
                
                client = TestClient(app)
                
                # Send multiple concurrent requests
                responses = []
                for i in range(5):
                    response = client.post("/api/webhook", data={
                        "From": f"whatsapp:+123456789{i}",
                        "Body": "I'd like to schedule a consultation",
                        "MessageSid": f"test-{i}",
                        "To": "whatsapp:+14155238886"
                    })
                    responses.append(response)
                
                # All requests should succeed
                for response in responses:
                    assert response.status_code == 200
                    assert "Response" in response.text
    
    def test_large_message_handling(self, mock_environment):
        """Test handling of large messages"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            mock_openai.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content="NO"))]
            )
            
            client = TestClient(app)
            
            # Test with very long message
            long_message = "This is a very long message. " * 100
            response = client.post("/api/webhook", data={
                "From": "whatsapp:+1234567890",
                "Body": long_message,
                "MessageSid": "test-1",
                "To": "whatsapp:+14155238886"
            })
            assert response.status_code == 200
            assert "Response" in response.text


@pytest.mark.e2e
class TestDataPersistence:
    """Test data persistence across requests"""
    
    def test_conversation_state_persistence(self, mock_environment):
        """Test that conversation state persists across multiple messages"""
        with patch('app.agents.manager_agent.openai_client') as mock_openai:
            with patch('app.agents.specialized_agents.scheduling_agent_2.openai_client') as mock_anna:
                # Mock responses
                mock_openai.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="YES"))]
                )
                mock_anna.chat.completions.create.return_value = Mock(
                    choices=[Mock(message=Mock(content="Hello! I'm Anna. Let's start with some questions."))]
                )
                
                client = TestClient(app)
                
                # First message
                response1 = client.post("/api/webhook", data={
                    "From": "whatsapp:+1234567890",
                    "Body": "I'd like to schedule a consultation",
                    "MessageSid": "test-1",
                    "To": "whatsapp:+14155238886"
                })
                assert response1.status_code == 200
                
                # Second message (should maintain context)
                response2 = client.post("/api/webhook", data={
                    "From": "whatsapp:+1234567890",
                    "Body": "yes",
                    "MessageSid": "test-2",
                    "To": "whatsapp:+14155238886"
                })
                assert response2.status_code == 200
                
                # Responses should be different and context-aware
                assert response1.text != response2.text

