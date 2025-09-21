"""
Integration tests for component interactions
These tests verify that different components work together correctly
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.agents.manager_agent import detect_scheduling_intent, run_manager
from app.agents.specialized_agents.scheduling_agent_2 import handle_scheduling_request
from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
from app.agents.specialized_agents.scheduling_models import ConversationState, SchedulingStep


@pytest.mark.integration
class TestIntentDetectionIntegration:
    """Test intent detection integration with manager agent"""
    
    @pytest.mark.asyncio
    async def test_scheduling_intent_detection(self, mock_openai_response):
        """Test scheduling intent detection with OpenAI integration"""
        with patch('app.services.openai_service.openai_service') as mock_service:
            mock_service.get_completion.return_value = mock_openai_response
            
            # Test clear scheduling intent
            result = await detect_scheduling_intent("I'd like to schedule a consultation")
            assert result is True
            
            # Test non-scheduling intent
            result = await detect_scheduling_intent("What treatments do you offer?")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_manager_agent_routing(self, mock_openai_response):
        """Test manager agent routes correctly based on intent"""
        with patch('app.services.openai_service.openai_service') as mock_service:
            mock_service.get_completion.return_value = mock_openai_response
            
            # Test routing to scheduling agent
            response = await run_manager("I'd like to schedule a consultation", "test_user")
            assert "Anna" in response or "consultation" in response.lower()
            
            # Test routing to language agent
            response = await run_manager("What treatments do you offer?", "test_user")
            assert response is not None


@pytest.mark.integration
class TestQuestionnaireIntegration:
    """Test questionnaire system integration"""
    
    @pytest.mark.asyncio
    async def test_questionnaire_flow_integration(self, sample_conversation_state):
        """Test complete questionnaire flow integration"""
        manager = QuestionnaireManager()
        
        # Start questionnaire
        result = manager.start_questionnaire(sample_conversation_state)
        assert "questions" in result.lower() or "questionnaire" in result.lower()
        
        # Process first response
        success, result, next_action = manager.process_response("basic_country", "United States", sample_conversation_state)
        assert success
        assert "move on" in result.lower() or "age" in result.lower()
        
        # Process second response
        success, result, next_action = manager.process_response("basic_age", "35", sample_conversation_state)
        assert success
        assert "move on" in result.lower() or "gender" in result.lower()
    
    @pytest.mark.asyncio
    async def test_questionnaire_skip_integration(self, sample_conversation_state):
        """Test questionnaire skip functionality integration"""
        manager = QuestionnaireManager()
        
        # Start questionnaire
        manager.start_questionnaire(sample_conversation_state)
        
        # Skip first question
        success, result, next_action = manager.process_response("basic_country", "skip", sample_conversation_state)
        assert success
        assert "move on" in result.lower()
        
        # Skip second question
        success, result, next_action = manager.process_response("basic_age", "skip", sample_conversation_state)
        assert success
        assert "move on" in result.lower()
    
    @pytest.mark.asyncio
    async def test_questionnaire_completion_integration(self, sample_conversation_state):
        """Test questionnaire completion integration"""
        manager = QuestionnaireManager()
        
        # Start questionnaire
        manager.start_questionnaire(sample_conversation_state)
        
        # Answer all questions
        question_responses = [
            ("basic_country", "United States"),  # country
            ("basic_age", "35"),                # age
            ("basic_gender", "Male"),           # gender
            ("medical_conditions", "Diabetes"), # medical conditions
            ("current_medications", "Metformin"), # medications
            ("recent_events", "COVID-19"),      # recent events
            ("hair_loss_onset", "2 years ago"), # hair loss onset
            ("hair_loss_location", "Crown area"), # hair loss location
            ("previous_treatments", "Minoxidil") # previous treatments
        ]
        
        for question_id, response in question_responses:
            success, result, next_action = manager.process_response(question_id, response, sample_conversation_state)
            if next_action == "complete" or "complete" in result.lower():
                break
        
        # Check completion
        assert manager.is_questionnaire_complete(sample_conversation_state)


@pytest.mark.integration
class TestSchedulingAgentIntegration:
    """Test scheduling agent integration with questionnaire"""
    
    @pytest.mark.asyncio
    async def test_anna_questionnaire_integration(self, mock_openai_response):
        """Test Anna's integration with questionnaire system"""
        with patch('app.services.openai_service.openai_service') as mock_service:
            mock_service.get_completion.return_value = mock_openai_response
            
            # Test initial scheduling request
            response = await handle_scheduling_request("I'd like to schedule a consultation", "test_user")
            assert "consultation" in response.lower()
            
            # Test questionnaire initiation
            response = await handle_scheduling_request("yes", "test_user")
            assert "questionnaire" in response.lower() or "questions" in response.lower()
    
    @pytest.mark.asyncio
    async def test_conversation_state_persistence(self, mock_openai_response):
        """Test conversation state persistence across messages"""
        with patch('app.services.openai_service.openai_service') as mock_service:
            mock_service.get_completion.return_value = mock_openai_response
            
            # First message
            response1 = await handle_scheduling_request("I'd like to schedule a consultation", "test_user")
            
            # Second message (should maintain context)
            response2 = await handle_scheduling_request("yes", "test_user")
            
            # Responses should be different and context-aware
            assert response1 != response2
            assert len(response1) > 0
            assert len(response2) > 0


@pytest.mark.integration
class TestDataModelIntegration:
    """Test data model integration across components"""
    
    def test_patient_profile_questionnaire_integration(self, sample_patient_profile):
        """Test patient profile integration with questionnaire responses"""
        from app.agents.specialized_agents.scheduling_models import QuestionnaireResponse
        
        # Add questionnaire response
        response = QuestionnaireResponse(
            question_id="basic_country",
            question_text="What's your country?",
            answer="United States"
        )
        sample_patient_profile.questionnaire_responses.append(response)
        
        # Check integration
        assert len(sample_patient_profile.questionnaire_responses) == 1
        assert sample_patient_profile.questionnaire_responses[0].answer == "United States"
    
    def test_conversation_state_questionnaire_integration(self, sample_conversation_state):
        """Test conversation state integration with questionnaire"""
        from app.agents.specialized_agents.scheduling_models import QuestionnaireStep
        
        # Update questionnaire step
        sample_conversation_state.questionnaire_step = QuestionnaireStep.BASIC_INFO
        sample_conversation_state.current_question_id = "basic_country"
        
        # Check integration
        assert sample_conversation_state.questionnaire_step == QuestionnaireStep.BASIC_INFO
        assert sample_conversation_state.current_question_id == "basic_country"


@pytest.mark.integration
class TestWebhookIntegration:
    """Test webhook integration with message processing"""
    
    def test_webhook_message_processing(self, test_app, sample_webhook_payload):
        """Test webhook processes messages correctly"""
        response = test_app.post("/api/webhook", data=sample_webhook_payload)
        
        # Should return XML response
        assert response.status_code == 200
        assert "Response" in response.text
        assert "Message" in response.text
    
    def test_webhook_error_handling(self, test_app):
        """Test webhook error handling"""
        # Test with invalid payload
        response = test_app.post("/api/webhook", data={})
        
        # Should handle error gracefully
        assert response.status_code == 200
        assert "Response" in response.text


@pytest.mark.integration
class TestCalendarIntegration:
    """Test Google Calendar integration"""
    
    def test_calendar_service_creation(self, mock_environment):
        """Test calendar service creation with mocked environment"""
        with patch('app.tools.google_calendar_tools.service_account.Credentials.from_service_account_info'):
            with patch('app.tools.google_calendar_tools.build'):
                from app.tools.google_calendar_tools import get_calendar_service
                service = get_calendar_service()
                assert service is not None
    
    def test_calendar_event_creation(self, mock_calendar_service):
        """Test calendar event creation"""
        from app.tools.google_calendar_tools import create_calendar_event
        
        with patch('app.tools.google_calendar_tools.get_calendar_service', return_value=mock_calendar_service):
            result = create_calendar_event.func(
                summary="Test Appointment",
                start_datetime="2024-12-20T15:00:00",
                duration_minutes=30,
                description="Test description",
                attendee_email="test@example.com"
            )
            assert "success" in result.lower() or "created" in result.lower()

