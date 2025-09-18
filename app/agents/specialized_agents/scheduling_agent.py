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
            if not current_profile.appointment_request:
                current_profile.appointment_request = AppointmentRequest()
            
            if not current_profile.appointment_request.preferred_date:
                current_profile.appointment_request.preferred_date = message.strip()
                return responses["time_preference"], current_profile, SchedulingStep.CONSULTATION_SCHEDULING
            
            elif not current_profile.appointment_request.preferred_time:
                current_profile.appointment_request.preferred_time = message.strip()
                return responses["scheduling_confirmation"], current_profile, SchedulingStep.ADDITIONAL_INFO
        
        elif step == SchedulingStep.ADDITIONAL_INFO:
            # Handle optional information collection
            if any(word in message.lower() for word in ["skip", "no", "nein", "no", "pass"]):
                return responses["closure_intro"], current_profile, SchedulingStep.CLOSURE
            else:
                # Collect optional info (simplified)
                if not current_profile.location:
                    current_profile.location = message.strip()
                    return responses["age_request"], current_profile, SchedulingStep.ADDITIONAL_INFO
                else:
                    return responses["closure_intro"], current_profile, SchedulingStep.CLOSURE
        
        return responses["error"], current_profile, step
    
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
            "age_request": "Thank you! What's your age? (This is optional - you can say 'skip' if you prefer not to share)",
            "closure_intro": "Great! To help our specialists prepare, I'd like to ask a few optional questions about your medical background. You can skip any you're not comfortable with, or say 'skip all' to proceed.",
            "validation_error": "I need all three pieces of information to proceed. Let me start over. What's your full name?",
            "error": "I apologize, but I'm having trouble processing that. Could you please try again?"
        }


# Factory function
def create_scheduling_service() -> SchedulingService:
    """Create a new scheduling service instance."""
    return SchedulingService()