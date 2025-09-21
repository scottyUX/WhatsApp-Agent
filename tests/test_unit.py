"""
Unit tests for core functionality
These tests are fast, isolated, and test individual components
"""
import pytest
from unittest.mock import Mock, patch
from app.agents.specialized_agents.scheduling_models import PatientProfile, QuestionnaireStep, QuestionnaireResponse
from app.agents.specialized_agents.questionnaire_questions import Question, get_question_by_id
from utils.validators import validate_email, validate_phone, validate_name


@pytest.mark.unit
class TestPatientProfile:
    """Test PatientProfile data model"""
    
    def test_patient_profile_creation(self, sample_patient_profile):
        """Test creating a patient profile"""
        assert sample_patient_profile.name == "John Doe"
        assert sample_patient_profile.phone == "+1234567890"
        assert sample_patient_profile.email == "john@example.com"
        assert sample_patient_profile.questionnaire_step == QuestionnaireStep.NOT_STARTED
    
    def test_patient_profile_to_dict(self, sample_patient_profile):
        """Test converting patient profile to dictionary"""
        profile_dict = sample_patient_profile.to_dict()
        assert profile_dict["name"] == "John Doe"
        assert profile_dict["phone"] == "+1234567890"
        assert profile_dict["email"] == "john@example.com"
        assert profile_dict["questionnaire_step"] == "not_started"
    
    def test_questionnaire_response_creation(self):
        """Test creating questionnaire response"""
        response = QuestionnaireResponse(
            question_id="test_question",
            question_text="Test question?",
            answer="Test answer"
        )
        assert response.question_id == "test_question"
        assert response.question_text == "Test question?"
        assert response.answer == "Test answer"
        assert not response.skipped
        assert not response.clarification_attempted


@pytest.mark.unit
class TestQuestionnaireQuestions:
    """Test questionnaire questions functionality"""
    
    def test_get_question_by_id(self):
        """Test getting question by ID"""
        question = get_question_by_id("basic_country")
        assert question is not None
        assert question.id == "basic_country"
        assert question.category == "basic_info"
    
    def test_get_nonexistent_question(self):
        """Test getting non-existent question"""
        question = get_question_by_id("nonexistent")
        assert question is None


@pytest.mark.unit
class TestValidators:
    """Test input validation functions"""
    
    def test_email_validation_valid(self):
        """Test valid email validation"""
        is_valid, error = validate_email("test@example.com")
        assert is_valid
        assert error is None
    
    def test_email_validation_invalid(self):
        """Test invalid email validation"""
        is_valid, error = validate_email("invalid-email")
        assert not is_valid
        assert error is not None
    
    def test_phone_validation_valid(self):
        """Test valid phone validation"""
        is_valid, error, formatted = validate_phone("+1234567890")
        assert is_valid
        assert formatted == "+1234567890"
    
    def test_phone_validation_invalid(self):
        """Test invalid phone validation"""
        is_valid, error, formatted = validate_phone("123")
        assert not is_valid
        assert error is not None
    
    def test_name_validation_valid(self):
        """Test valid name validation"""
        is_valid, error = validate_name("John Doe")
        assert is_valid
        assert error is None
    
    def test_name_validation_invalid(self):
        """Test invalid name validation"""
        is_valid, error = validate_name("")
        assert not is_valid
        assert error is not None


@pytest.mark.unit
class TestQuestionnaireManager:
    """Test questionnaire manager core functionality"""
    
    def test_questionnaire_manager_initialization(self):
        """Test questionnaire manager initialization"""
        from app.agents.specialized_agents.questionnaire_manager import QuestionnaireManager
        
        manager = QuestionnaireManager()
        assert manager is not None
        assert len(manager.question_categories) == 3  # basic, medical, hair_loss
    
    def test_start_questionnaire(self, mock_questionnaire_manager, sample_conversation_state):
        """Test starting questionnaire"""
        result = mock_questionnaire_manager.start_questionnaire(sample_conversation_state)
        assert "questions" in result.lower() or "questionnaire" in result.lower()
        # Check that questionnaire step was updated
        assert sample_conversation_state.patient_profile.questionnaire_step == QuestionnaireStep.BASIC_INFO
    
    def test_process_response_skip(self, mock_questionnaire_manager, sample_conversation_state):
        """Test processing skip response"""
        # Set a current question ID first
        sample_conversation_state.current_question_id = "basic_country"
        success, message, next_action = mock_questionnaire_manager.process_response("basic_country", "skip", sample_conversation_state)
        assert success
        assert "move on" in message.lower() or "next" in message.lower()
    
    def test_is_questionnaire_complete(self, mock_questionnaire_manager, sample_conversation_state):
        """Test questionnaire completion check"""
        # Initially not complete
        assert not mock_questionnaire_manager.is_questionnaire_complete(sample_conversation_state)
        
        # Mock completion by setting the questionnaire step to completed
        sample_conversation_state.patient_profile.questionnaire_step = QuestionnaireStep.COMPLETED
        assert mock_questionnaire_manager.is_questionnaire_complete(sample_conversation_state)


@pytest.mark.unit
class TestSchedulingModels:
    """Test scheduling models and enums"""
    
    def test_questionnaire_step_enum(self):
        """Test questionnaire step enum values"""
        from app.agents.specialized_agents.scheduling_models import QuestionnaireStep
        
        assert QuestionnaireStep.NOT_STARTED.value == "not_started"
        assert QuestionnaireStep.BASIC_INFO.value == "basic_info"
        assert QuestionnaireStep.MEDICAL_INFO.value == "medical_info"
        assert QuestionnaireStep.HAIR_LOSS_INFO.value == "hair_loss_info"
        assert QuestionnaireStep.COMPLETED.value == "completed"
        assert QuestionnaireStep.SKIPPED.value == "skipped"
    
    def test_scheduling_step_enum(self):
        """Test scheduling step enum values"""
        from app.agents.specialized_agents.scheduling_models import SchedulingStep
        
        assert SchedulingStep.INITIAL_CONTACT.value == "initial_contact"
        assert SchedulingStep.BASIC_INFO.value == "basic_info"
        assert SchedulingStep.CONSULTATION_SCHEDULING.value == "consultation_scheduling"
        assert SchedulingStep.ADDITIONAL_INFO.value == "additional_info"
        assert SchedulingStep.QUESTIONNAIRE.value == "questionnaire"
        assert SchedulingStep.CLOSURE.value == "closure"


@pytest.mark.unit
class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_question_skip_detection(self):
        """Test skip response detection"""
        from app.agents.specialized_agents.questionnaire_questions import is_skip_response
        
        assert is_skip_response("skip")
        assert is_skip_response("SKIP")
        assert is_skip_response("Skip")
        assert is_skip_response("pass")
        assert is_skip_response("next")
        assert not is_skip_response("yes")
        assert not is_skip_response("no")
        assert not is_skip_response("maybe")
    
    def test_question_category_filtering(self):
        """Test filtering questions by category"""
        from app.agents.specialized_agents.questionnaire_questions import get_questions_by_category
        
        basic_questions = get_questions_by_category("basic_info")
        assert len(basic_questions) == 3  # country, age, gender
        
        medical_questions = get_questions_by_category("medical_info")
        assert len(medical_questions) == 3  # conditions, medications, recent events
        
        hair_loss_questions = get_questions_by_category("hair_loss_info")
        assert len(hair_loss_questions) == 3  # onset, location, treatments

