"""
Scheduling Service for Istanbul Medic
A service that helps language agents handle consultation scheduling.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

from .scheduling_models import (
    PatientProfile, 
    AppointmentRequest, 
    SchedulingStep,
    BookingError,
    CRMError,
    NotificationError
)
from .questionnaire_manager import create_questionnaire_manager
from .scheduling_services import (
    GoogleCalendarService,
    HubSpotService,
    NotificationService
)

logger = logging.getLogger(__name__)


class SchedulingService:
    """
    Service for handling consultation scheduling.
    Called by language agents when scheduling intent is detected.
    """
    
    def __init__(self):
        # Initialize services
        self.calendar_service = GoogleCalendarService()
        self.crm_service = HubSpotService()
        self.notification_service = NotificationService()
        self.questionnaire_manager = create_questionnaire_manager()
    
    async def detect_scheduling_intent(self, message: str, language: str = "en") -> bool:
        """
        Detect if the user wants to schedule a consultation.
        Returns True if scheduling intent is detected.
        """
        scheduling_keywords = {
            "en": [
                "schedule", "book", "appointment", "consultation", "meeting",
                "available", "time", "date", "calendar", "reserve", "set up"
            ],
            "de": [
                "termin", "buchung", "beratung", "treffen", "verfügbar",
                "zeit", "datum", "kalender", "reservieren", "vereinbaren"
            ],
            "es": [
                "programar", "reservar", "cita", "consulta", "reunión",
                "disponible", "hora", "fecha", "calendario", "agendar"
            ]
        }
        
        keywords = scheduling_keywords.get(language, scheduling_keywords["en"])
        message_lower = message.lower()
        
        return any(keyword in message_lower for keyword in keywords)
    
    async def collect_patient_info(self, message: str, current_profile: PatientProfile, step: SchedulingStep) -> Tuple[str, PatientProfile, SchedulingStep]:
        """
        Collect patient information step by step.
        Returns: (response_message, updated_profile, next_step)
        """
        responses = self._get_responses()
        
        if step == SchedulingStep.INITIAL_CONTACT:
            return responses["consent_request"], current_profile, SchedulingStep.BASIC_INFO
        
        elif step == SchedulingStep.BASIC_INFO:
            if not current_profile.name:
                current_profile.name = message.strip()
                return responses["phone_request"], current_profile, SchedulingStep.BASIC_INFO
            
            elif not current_profile.phone:
                current_profile.phone = message.strip()
                return responses["email_request"], current_profile, SchedulingStep.BASIC_INFO
            
            elif not current_profile.email:
                current_profile.email = message.strip()
                
                # Validate required fields
                if self._validate_required_fields(current_profile):
                    return responses["scheduling_intro"], current_profile, SchedulingStep.CONSULTATION_SCHEDULING
                else:
                    return responses["validation_error"], current_profile, SchedulingStep.BASIC_INFO
        
        elif step == SchedulingStep.CONSULTATION_SCHEDULING:
            # Initialize appointment request if not exists
            if current_profile.appointment_request is None:
                current_profile.appointment_request = AppointmentRequest()
            
            if not current_profile.appointment_request.preferred_date:
                current_profile.appointment_request.preferred_date = message.strip()
                return responses["time_preference"], current_profile, SchedulingStep.CONSULTATION_SCHEDULING
            
            elif not current_profile.appointment_request.preferred_time:
                current_profile.appointment_request.preferred_time = message.strip()
                return responses["scheduling_confirmation"], current_profile, SchedulingStep.QUESTIONNAIRE
        
        elif step == SchedulingStep.QUESTIONNAIRE:
            # Handle questionnaire using the questionnaire manager
            return await self._handle_questionnaire(message, current_profile)
        
        return responses["error"], current_profile, step
    
    async def _handle_questionnaire(self, message: str, current_profile: PatientProfile) -> Tuple[str, PatientProfile, SchedulingStep]:
        """
        Handle questionnaire step using the questionnaire manager.
        """
        # Check if questionnaire has started
        if not current_profile.questionnaire_step or current_profile.questionnaire_step.value == "not_started":
            # Start questionnaire
            from .scheduling_models import ConversationState
            conversation_state = ConversationState(
                user_id="temp_user",  # This would come from the actual user context
                phone_number=current_profile.phone,
                current_step=SchedulingStep.QUESTIONNAIRE,
                patient_profile=current_profile
            )
            
            start_message = self.questionnaire_manager.start_questionnaire(conversation_state)
            # Update the profile with the questionnaire state
            current_profile.questionnaire_step = conversation_state.patient_profile.questionnaire_step
            current_profile.questionnaire_started_at = conversation_state.questionnaire_started_at
            return start_message, current_profile, SchedulingStep.QUESTIONNAIRE
        
        # Process user response
        from .scheduling_models import ConversationState
        conversation_state = ConversationState(
            user_id="temp_user",
            phone_number=current_profile.phone,
            current_step=SchedulingStep.QUESTIONNAIRE,
            patient_profile=current_profile
        )
        
        # Set the current question ID from the profile
        conversation_state.current_question_id = getattr(current_profile, 'current_question_id', None)
        
        success, response_message, next_action = self.questionnaire_manager.process_response(
            conversation_state.current_question_id,
            message,
            conversation_state,
            save_to_db=False
        )
        
        # Update the profile with any changes from the questionnaire manager
        current_profile.questionnaire_responses = conversation_state.patient_profile.questionnaire_responses
        current_profile.questionnaire_step = conversation_state.patient_profile.questionnaire_step
        current_profile.questionnaire_completed_at = conversation_state.patient_profile.questionnaire_completed_at
        current_profile.current_question_id = conversation_state.current_question_id
        
        if next_action == "complete":
            # Questionnaire complete
            return response_message, current_profile, SchedulingStep.CLOSURE
        elif next_action == "clarify":
            # Ask for clarification
            return response_message, current_profile, SchedulingStep.QUESTIONNAIRE
        else:
            # Get next question
            next_question = self.questionnaire_manager.get_next_question(conversation_state)
            if next_question:
                # Update conversation state with current question
                conversation_state.current_question_id = next_question["id"]
                current_profile.current_question_id = next_question["id"]
                return next_question["text"], current_profile, SchedulingStep.QUESTIONNAIRE
            else:
                # No more questions, questionnaire complete
                return "Perfect! I've collected all the information. Our specialists will review this before your consultation.", current_profile, SchedulingStep.CLOSURE
    
    async def book_appointment(self, patient_profile: PatientProfile) -> Dict[str, Any]:
        """
        Book the appointment and create lead.
        Returns appointment details or raises an error.
        """
        try:
            # Book appointment in Google Calendar
            appointment = await self.calendar_service.create_appointment(
                patient_profile, 
                patient_profile.appointment_request
            )
            
            if not appointment:
                raise BookingError("Failed to create appointment")
            
            # Create lead in HubSpot
            try:
                lead_id = await self.crm_service.create_lead(patient_profile)
                appointment["lead_id"] = lead_id
            except Exception as e:
                logger.warning(f"Failed to create lead in HubSpot: {e}")
                appointment["lead_id"] = None
            
            # Send confirmations
            try:
                await self.notification_service.send_confirmation(
                    patient_profile.phone,
                    patient_profile.email,
                    patient_profile.appointment_request
                )
            except Exception as e:
                logger.warning(f"Failed to send confirmation: {e}")
            
            return appointment
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            raise BookingError(f"Failed to book appointment: {e}")
    
    def _validate_required_fields(self, profile: PatientProfile) -> bool:
        """Validate that all required fields are present."""
        return all([
            profile.name and len(profile.name.strip()) > 0,
            profile.phone and len(profile.phone.strip()) > 0,
            profile.email and "@" in profile.email
        ])
    
    def _get_responses(self) -> Dict[str, str]:
        """Get language-specific responses."""
        return {
            "consent_request": "I'll need to collect some basic information to book your consultation. This includes your name, phone number, and email address. Is that okay with you?",
            "name_request": "Perfect! Let's start with your full name, please.",
            "phone_request": "Thank you! Now, could you please provide your phone number?",
            "email_request": "Great! And your email address?",
            "scheduling_intro": "Excellent! Now let's find a convenient time for your consultation. What day works best for you?",
            "time_preference": "Would you prefer morning or afternoon?",
            "scheduling_confirmation": "Perfect! I've scheduled your consultation. You'll receive a confirmation by email and SMS with all the details.",
            "validation_error": "I need all three pieces of information to proceed. Let me start over. What's your full name?",
            "error": "I apologize, but I'm having trouble processing that. Could you please try again?"
        }


# Factory function
def create_scheduling_service() -> SchedulingService:
    """Create a new scheduling service instance."""
    return SchedulingService()