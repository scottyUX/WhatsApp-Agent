"""
External service integrations for the scheduling agent.
Handles Google Calendar, HubSpot CRM, and notification services.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import json

# Google Calendar imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# HubSpot imports
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.companies import SimplePublicObjectInput as CompanyInput

# Twilio for SMS
from twilio.rest import Client as TwilioClient

from .scheduling_models import (
    PatientProfile, 
    AppointmentRequest, 
    AppointmentResponse,
    LeadResponse,
    NotificationRequest,
    BookingError,
    CRMError,
    NotificationError
)

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for managing Google Calendar appointments."""
    
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        self.credentials_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE")
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service with OAuth2 credentials."""
        try:
            if not self.credentials_file or not os.path.exists(self.credentials_file):
                logger.warning("Google Calendar credentials file not found")
                return
            
            # Load credentials
            creds = None
            token_file = 'token.json'
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, 
                        ['https://www.googleapis.com/auth/calendar']
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    async def create_appointment(
        self, 
        patient: PatientProfile, 
        appointment_request: AppointmentRequest
    ) -> Optional[Dict[str, Any]]:
        """Create a new appointment in Google Calendar."""
        if not self.service:
            raise BookingError("Google Calendar service not available")
        
        try:
            # Parse appointment datetime
            scheduled_datetime = self._parse_appointment_datetime(
                appointment_request.preferred_date,
                appointment_request.preferred_time,
                appointment_request.time_zone
            )
            
            # Create calendar event
            event = {
                'summary': f'Consultation - {patient.name}',
                'description': f'Free consultation with Istanbul Medic specialist\n\nPatient: {patient.name}\nPhone: {patient.phone}\nEmail: {patient.email}',
                'start': {
                    'dateTime': scheduled_datetime.isoformat(),
                    'timeZone': appointment_request.time_zone,
                },
                'end': {
                    'dateTime': (scheduled_datetime + timedelta(minutes=appointment_request.duration_minutes)).isoformat(),
                    'timeZone': appointment_request.time_zone,
                },
                'attendees': [
                    {'email': patient.email, 'displayName': patient.name},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},       # 30 minutes before
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'consultation-{patient.phone}-{int(scheduled_datetime.timestamp())}',
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Appointment created: {created_event['id']}")
            
            return {
                "appointment_id": created_event['id'],
                "calendar_event_id": created_event['id'],
                "scheduled_datetime": scheduled_datetime,
                "time_zone": appointment_request.time_zone,
                "duration_minutes": appointment_request.duration_minutes,
                "status": "scheduled",
                "confirmation_code": self._generate_confirmation_code(),
                "meeting_link": created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise BookingError(f"Failed to create appointment: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating appointment: {e}")
            raise BookingError(f"Unexpected error: {e}")
    
    def _parse_appointment_datetime(self, date_str: str, time_str: str, timezone: str) -> datetime:
        """Parse appointment date and time into datetime object."""
        # This is a simplified parser - in production, you'd want more robust date parsing
        try:
            # Combine date and time
            datetime_str = f"{date_str} {time_str}"
            
            # Parse based on common formats
            for fmt in ['%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M', '%d/%m/%Y %H:%M']:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, try to parse naturally
            # This would ideally use a library like dateutil
            raise ValueError(f"Unable to parse date/time: {date_str} {time_str}")
            
        except Exception as e:
            raise BookingError(f"Invalid date/time format: {e}")
    
    def _generate_confirmation_code(self) -> str:
        """Generate a confirmation code for the appointment."""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class HubSpotService:
    """Service for managing leads in HubSpot CRM."""
    
    def __init__(self):
        self.access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.portal_id = os.getenv("HUBSPOT_PORTAL_ID")
        self.client = None
        
        if self.access_token:
            self.client = HubSpot(access_token=self.access_token)
    
    async def create_lead(self, patient: PatientProfile) -> str:
        """Create a new lead in HubSpot."""
        if not self.client:
            raise CRMError("HubSpot client not initialized")
        
        try:
            # Prepare contact data
            contact_data = {
                "firstname": patient.name.split()[0] if patient.name else "",
                "lastname": " ".join(patient.name.split()[1:]) if len(patient.name.split()) > 1 else "",
                "email": patient.email,
                "phone": patient.phone,
                "city": patient.location,
                "lifecyclestage": "lead",
                "lead_status": "new",
                "hs_lead_status": "NEW",
                "lead_source": "whatsapp_scheduling",
                "notes_last_contacted": f"Scheduled consultation via WhatsApp on {datetime.now().strftime('%Y-%m-%d')}",
            }
            
            # Add optional fields if available
            if patient.age:
                contact_data["age"] = str(patient.age)
            
            if patient.gender:
                contact_data["gender"] = patient.gender.value
            
            # Create contact
            contact_input = SimplePublicObjectInput(properties=contact_data)
            created_contact = self.client.crm.contacts.basic_api.create(contact_input)
            
            logger.info(f"Lead created in HubSpot: {created_contact.id}")
            return created_contact.id
            
        except Exception as e:
            logger.error(f"Failed to create lead in HubSpot: {e}")
            raise CRMError(f"Failed to create lead: {e}")
    
    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing lead in HubSpot."""
        if not self.client:
            raise CRMError("HubSpot client not initialized")
        
        try:
            contact_input = SimplePublicObjectInput(properties=updates)
            self.client.crm.contacts.basic_api.update(
                contact_id=lead_id,
                simple_public_object_input=contact_input
            )
            
            logger.info(f"Lead updated in HubSpot: {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lead in HubSpot: {e}")
            raise CRMError(f"Failed to update lead: {e}")


class NotificationService:
    """Service for sending SMS and email notifications."""
    
    def __init__(self):
        self.twilio_client = None
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio if credentials are available
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if account_sid and auth_token:
            self.twilio_client = TwilioClient(account_sid, auth_token)
    
    async def send_confirmation(
        self, 
        phone_number: str, 
        email: str, 
        appointment_request: AppointmentRequest
    ) -> bool:
        """Send confirmation SMS and email."""
        try:
            # Send SMS confirmation
            if self.twilio_client and phone_number:
                await self._send_sms_confirmation(phone_number, appointment_request)
            
            # Send email confirmation
            if email:
                await self._send_email_confirmation(email, appointment_request)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send confirmation: {e}")
            raise NotificationError(f"Failed to send confirmation: {e}")
    
    async def _send_sms_confirmation(self, phone_number: str, appointment_request: AppointmentRequest):
        """Send SMS confirmation."""
        if not self.twilio_client:
            logger.warning("Twilio client not available for SMS")
            return
        
        message_body = f"""
Istanbul Medic - Consultation Confirmed

Your free consultation has been scheduled for:
Date: {appointment_request.preferred_date}
Time: {appointment_request.preferred_time}

You'll receive a calendar invite with the meeting link shortly.

Thank you for choosing Istanbul Medic!
        """.strip()
        
        try:
            self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=phone_number
            )
            logger.info(f"SMS confirmation sent to {phone_number}")
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise NotificationError(f"SMS sending failed: {e}")
    
    async def _send_email_confirmation(self, email: str, appointment_request: AppointmentRequest):
        """Send email confirmation."""
        # This is a placeholder - in production, you'd use an email service
        # like SendGrid, AWS SES, or similar
        logger.info(f"Email confirmation would be sent to {email}")
        
        # For now, just log the email content
        email_content = f"""
Subject: Istanbul Medic - Consultation Confirmed

Dear Patient,

Your free consultation has been scheduled for:
Date: {appointment_request.preferred_date}
Time: {appointment_request.preferred_time}

You'll receive a calendar invite with the meeting link shortly.

Thank you for choosing Istanbul Medic!

Best regards,
Anna - Consultation Assistant
        """.strip()
        
        logger.info(f"Email content: {email_content}")


# Factory functions
def create_calendar_service() -> GoogleCalendarService:
    """Create a new Google Calendar service instance."""
    return GoogleCalendarService()


def create_crm_service() -> HubSpotService:
    """Create a new HubSpot CRM service instance."""
    return HubSpotService()


def create_notification_service() -> NotificationService:
    """Create a new notification service instance."""
    return NotificationService()
