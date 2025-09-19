"""
Questionnaire Manager for handling patient intake questions.
Manages question flow, response processing, and skip handling.
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from .scheduling_models import (
    QuestionnaireStep, 
    QuestionnaireResponse, 
    PatientProfile, 
    ConversationState
)
from .questionnaire_questions import (
    ALL_QUESTIONS,
    QUESTION_CATEGORIES,
    get_question_by_id,
    get_questions_by_category,
    get_next_question_id,
    is_skip_response
)


class QuestionnaireManager:
    """Manages the questionnaire flow and response processing."""
    
    def __init__(self):
        self.question_categories = ["basic", "medical", "hair_loss"]
        self.current_category_index = 0
    
    def get_next_question(self, conversation_state: ConversationState) -> Optional[Dict[str, Any]]:
        """
        Get the next question to ask based on current state.
        
        Args:
            conversation_state: Current conversation state
            
        Returns:
            Question data or None if questionnaire is complete
        """
        # Check if questionnaire is already completed or skipped
        if conversation_state.patient_profile.questionnaire_step in [QuestionnaireStep.COMPLETED, QuestionnaireStep.SKIPPED]:
            return None
        
        # Get current category
        current_category = self._get_current_category(conversation_state)
        if not current_category:
            return None
        
        # Get current question ID
        current_question_id = conversation_state.current_question_id
        
        if current_question_id:
            # Get next question in current category
            next_question_id = get_next_question_id(current_question_id, current_category)
            if next_question_id:
                question = get_question_by_id(next_question_id)
                if question:
                    conversation_state.current_question_id = next_question_id
                    return self._format_question(question)
            
            # Move to next category
            if self._move_to_next_category():
                question = self._get_first_question_in_category(conversation_state)
                if question:
                    conversation_state.current_question_id = question["id"]
                return question
        else:
            # Start with first question in current category
            question = self._get_first_question_in_category(conversation_state)
            if question:
                # Set the current question ID in the conversation state
                conversation_state.current_question_id = question["id"]
            return question
        
        # No more questions
        return None
    
    def process_response(self, 
                        question_id: str, 
                        user_response: str, 
                        conversation_state: ConversationState,
                        save_to_db: bool = False) -> Tuple[bool, str, str]:
        """
        Process user response to a question.
        
        Args:
            question_id: ID of the question being answered
            user_response: User's response text
            conversation_state: Current conversation state
            save_to_db: Whether to save responses to database immediately
            
        Returns:
            Tuple of (success, message, next_action)
            - success: Whether processing was successful
            - message: Response message to send to user
            - next_action: What to do next ('continue', 'clarify', 'complete')
        """
        question = get_question_by_id(question_id)
        if not question:
            return False, "I'm sorry, I couldn't find that question.", "continue"
        
        # Check if user wants to skip
        if is_skip_response(user_response):
            return self._handle_skip(question, conversation_state)
        
        # Check if response needs clarification
        if self._needs_clarification(question, user_response):
            return self._handle_clarification(question, conversation_state)
        
        # Process the response
        return self._handle_response(question, user_response, conversation_state)
    
    def start_questionnaire(self, conversation_state: ConversationState) -> str:
        """
        Start the questionnaire process.
        
        Args:
            conversation_state: Current conversation state
            
        Returns:
            Welcome message for questionnaire
        """
        conversation_state.patient_profile.questionnaire_step = QuestionnaireStep.BASIC_INFO
        conversation_state.questionnaire_started_at = datetime.now()
        
        # Get the first question and set it as current
        first_question = self.get_next_question(conversation_state)
        
        welcome_message = ("Great! To help our specialists prepare for your consultation, I'd like to ask you a few optional questions. " +
                          "You can skip any question you're not comfortable with. Let's start with some basic information.")
        
        if first_question:
            return f"{welcome_message}\n\n{first_question['text']}"
        else:
            return welcome_message
    
    def is_questionnaire_complete(self, conversation_state: ConversationState) -> bool:
        """Check if questionnaire is complete."""
        return conversation_state.patient_profile.questionnaire_step == QuestionnaireStep.COMPLETED
    
    def save_responses_to_database(self, conversation_state: ConversationState) -> bool:
        """
        Save all questionnaire responses to database.
        
        Args:
            conversation_state: Current conversation state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would integrate with your database service
            # For now, we'll just mark that responses are ready to be saved
            conversation_state.patient_profile.questionnaire_step = QuestionnaireStep.COMPLETED
            conversation_state.patient_profile.questionnaire_completed_at = datetime.now()
            
            # TODO: Implement actual database saving
            # Example:
            # for response in conversation_state.patient_profile.questionnaire_responses:
            #     save_questionnaire_response(response, conversation_state.user_id)
            
            return True
        except Exception as e:
            print(f"Error saving questionnaire responses: {e}")
            return False
    
    def _get_current_category(self, conversation_state: ConversationState) -> Optional[str]:
        """Get the current category based on questionnaire step."""
        step = conversation_state.patient_profile.questionnaire_step
        
        if step == QuestionnaireStep.BASIC_INFO:
            return "basic"
        elif step == QuestionnaireStep.MEDICAL_INFO:
            return "medical"
        elif step == QuestionnaireStep.HAIR_LOSS_INFO:
            return "hair_loss"
        
        return None
    
    def _get_first_question_in_category(self, conversation_state: ConversationState) -> Optional[Dict[str, Any]]:
        """Get the first unanswered question in the current category."""
        current_category = self.question_categories[self.current_category_index]
        questions = get_questions_by_category(current_category)
        
        # Find first unanswered question
        for question in questions:
            if not self._get_existing_response(question.id, conversation_state):
                return self._format_question(question)
        
        return None
    
    def _format_question(self, question) -> Dict[str, Any]:
        """Format question for display."""
        return {
            "id": question.id,
            "text": question.text,
            "category": question.category,
            "skip_keywords": question.skip_keywords
        }
    
    def _move_to_next_category(self) -> bool:
        """Move to the next category."""
        self.current_category_index += 1
        return self.current_category_index < len(self.question_categories)
    
    def _needs_clarification(self, question, user_response: str) -> bool:
        """Check if response needs clarification."""
        # Simple heuristic: very short responses or unclear responses
        response_lower = user_response.lower().strip()
        
        # Check for unclear responses
        unclear_responses = ["i don't know", "not sure", "maybe", "i think", "probably"]
        if any(phrase in response_lower for phrase in unclear_responses):
            return True
        
        # Check for very short responses (less than 2 characters)
        if len(response_lower) < 2:
            return True
        
        return False
    
    def _handle_skip(self, question, conversation_state: ConversationState) -> Tuple[bool, str, str]:
        """Handle when user skips a question."""
        # Create skipped response
        response = QuestionnaireResponse(
            question_id=question.id,
            question_text=question.text,
            answer=None,
            skipped=True,
            clarification_attempted=False
        )
        
        # Add to patient profile
        conversation_state.patient_profile.questionnaire_responses.append(response)
        
        # Don't clear current_question_id here - let get_next_question handle it
        
        return True, "No problem! Let's move on.", "continue"
    
    def _handle_clarification(self, question, conversation_state: ConversationState) -> Tuple[bool, str, str]:
        """Handle when response needs clarification."""
        # Check if we've already asked for clarification
        existing_response = self._get_existing_response(question.id, conversation_state)
        
        if existing_response and existing_response.clarification_attempted:
            # Already asked for clarification, accept the response as-is
            return self._handle_response(question, conversation_state.current_question_id, conversation_state)
        
        # Ask for clarification
        if existing_response:
            existing_response.clarification_attempted = True
        else:
            # Create new response with clarification flag
            response = QuestionnaireResponse(
                question_id=question.id,
                question_text=question.text,
                answer=None,
                skipped=False,
                clarification_attempted=True
            )
            conversation_state.patient_profile.questionnaire_responses.append(response)
        
        return True, question.clarification_prompt, "clarify"
    
    def _handle_response(self, question, user_response: str, conversation_state: ConversationState) -> Tuple[bool, str, str]:
        """Handle normal response processing."""
        # Create or update response
        existing_response = self._get_existing_response(question.id, conversation_state)
        
        if existing_response:
            existing_response.answer = user_response
            existing_response.skipped = False
        else:
            response = QuestionnaireResponse(
                question_id=question.id,
                question_text=question.text,
                answer=user_response,
                skipped=False,
                clarification_attempted=False
            )
            conversation_state.patient_profile.questionnaire_responses.append(response)
        
        # Check if we should move to next category
        if self._should_move_to_next_category(question.category, conversation_state):
            self._move_to_next_category()
            conversation_state.patient_profile.questionnaire_step = self._get_next_questionnaire_step()
        
        # Check if questionnaire is complete
        if self._is_questionnaire_complete(conversation_state):
            # Save all responses to database
            self.save_responses_to_database(conversation_state)
            conversation_state.patient_profile.questionnaire_step = QuestionnaireStep.COMPLETED
            conversation_state.patient_profile.questionnaire_completed_at = datetime.now()
            return True, "Perfect! I've collected all the information. Our specialists will review this before your consultation.", "complete"
        
        # Clear current question ID so get_next_question can determine the next one
        conversation_state.current_question_id = None
        
        return True, "Let's move on.", "continue"
    
    def _get_existing_response(self, question_id: str, conversation_state: ConversationState) -> Optional[QuestionnaireResponse]:
        """Get existing response for a question."""
        for response in conversation_state.patient_profile.questionnaire_responses:
            if response.question_id == question_id:
                return response
        return None
    
    def _should_move_to_next_category(self, current_category: str, conversation_state: ConversationState) -> bool:
        """Check if we should move to the next category."""
        questions = get_questions_by_category(current_category)
        answered_questions = [r.question_id for r in conversation_state.patient_profile.questionnaire_responses 
                            if r.question_id in [q.id for q in questions]]
        
        return len(answered_questions) >= len(questions)
    
    def _get_next_questionnaire_step(self) -> QuestionnaireStep:
        """Get the next questionnaire step."""
        if self.current_category_index == 1:
            return QuestionnaireStep.MEDICAL_INFO
        elif self.current_category_index == 2:
            return QuestionnaireStep.HAIR_LOSS_INFO
        else:
            return QuestionnaireStep.COMPLETED
    
    def _is_questionnaire_complete(self, conversation_state: ConversationState) -> bool:
        """Check if questionnaire is complete."""
        return self.current_category_index >= len(self.question_categories)


# Factory function
def create_questionnaire_manager() -> QuestionnaireManager:
    """Create a new questionnaire manager instance."""
    return QuestionnaireManager()
