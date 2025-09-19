"""
Data models for the scheduling agent.
Defines the structure for patient profiles, appointments, and conversation states.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, EmailStr, validator


class SchedulingStep(Enum):
    """Enumeration of conversation steps in the scheduling process."""
    INITIAL_CONTACT = "initial_contact"
    BASIC_INFO = "basic_info"
    CONSULTATION_SCHEDULING = "consultation_scheduling"
    ADDITIONAL_INFO = "additional_info"
    QUESTIONNAIRE = "questionnaire"  # New step for questionnaire
    CLOSURE = "closure"


class QuestionnaireStep(Enum):
    """Enumeration of steps in the questionnaire process."""
    NOT_STARTED = "not_started"
    BASIC_INFO = "basic_info"
    MEDICAL_INFO = "medical_info"
    HAIR_LOSS_INFO = "hair_loss_info"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class AppointmentStatus(Enum):
    """Status of an appointment."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Gender(Enum):
    """Gender options for patient profiles."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


@dataclass
class QuestionnaireResponse:
    """Individual questionnaire response with metadata."""
    question_id: str
    question_text: str
    answer: Optional[str] = None
    skipped: bool = False
    clarification_attempted: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "answer": self.answer,
            "skipped": self.skipped,
            "clarification_attempted": self.clarification_attempted,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AppointmentRequest:
    """Appointment scheduling request."""
    preferred_date: str = ""
    preferred_time: str = ""
    time_zone: str = "UTC"
    duration_minutes: int = 60
    notes: str = ""
    
    # Calculated fields
    scheduled_datetime: Optional[datetime] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "preferred_date": self.preferred_date,
            "preferred_time": self.preferred_time,
            "time_zone": self.time_zone,
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
            "scheduled_datetime": self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            "status": self.status.value
        }


@dataclass
class PatientProfile:
    """Patient profile containing all collected information."""
    # Required fields
    name: str = ""
    phone: str = ""
    email: str = ""
    
    # Optional fields
    location: str = ""
    age: Optional[int] = None
    gender: Optional[Gender] = None
    
    # Medical background (optional)
    chronic_illnesses: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    surgeries: List[str] = field(default_factory=list)
    heart_conditions: List[str] = field(default_factory=list)
    contagious_diseases: List[str] = field(default_factory=list)
    
    # Hair loss background (optional)
    hair_loss_locations: List[str] = field(default_factory=list)  # crown, hairline, top
    hair_loss_start: Optional[str] = None
    family_history: Optional[bool] = None
    previous_treatments: List[str] = field(default_factory=list)
    
    # Questionnaire tracking
    questionnaire_responses: List[QuestionnaireResponse] = field(default_factory=list)
    questionnaire_step: QuestionnaireStep = QuestionnaireStep.NOT_STARTED
    questionnaire_started_at: Optional[datetime] = None
    questionnaire_completed_at: Optional[datetime] = None
    current_question_id: Optional[str] = None
    
    # Appointment request
    appointment_request: Optional[AppointmentRequest] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "location": self.location,
            "age": self.age,
            "gender": self.gender.value if self.gender else None,
            "chronic_illnesses": self.chronic_illnesses,
            "current_medications": self.current_medications,
            "allergies": self.allergies,
            "surgeries": self.surgeries,
            "heart_conditions": self.heart_conditions,
            "contagious_diseases": self.contagious_diseases,
            "hair_loss_locations": self.hair_loss_locations,
            "hair_loss_start": self.hair_loss_start,
            "family_history": self.family_history,
            "previous_treatments": self.previous_treatments,
            "questionnaire_responses": [response.to_dict() for response in self.questionnaire_responses],
            "questionnaire_step": self.questionnaire_step.value,
            "questionnaire_completed_at": self.questionnaire_completed_at.isoformat() if self.questionnaire_completed_at else None,
            "appointment_request": self.appointment_request.to_dict() if self.appointment_request else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class ConversationState:
    """Tracks the state of a conversation with a user."""
    user_id: str
    phone_number: str
    current_step: SchedulingStep
    patient_profile: PatientProfile = field(default_factory=PatientProfile)
    appointment_request: AppointmentRequest = field(default_factory=AppointmentRequest)
    lead_id: Optional[str] = None
    
    # Questionnaire tracking
    current_question_id: Optional[str] = None
    questionnaire_started_at: Optional[datetime] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "current_step": self.current_step.value,
            "patient_profile": self.patient_profile.to_dict(),
            "appointment_request": self.appointment_request.to_dict(),
            "lead_id": self.lead_id,
            "current_question_id": self.current_question_id,
            "questionnaire_started_at": self.questionnaire_started_at.isoformat() if self.questionnaire_started_at else None,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }


class AppointmentResponse(BaseModel):
    """Response model for appointment creation."""
    appointment_id: str
    calendar_event_id: str
    scheduled_datetime: datetime
    time_zone: str
    duration_minutes: int
    status: AppointmentStatus
    confirmation_code: str
    
    class Config:
        use_enum_values = True


class LeadResponse(BaseModel):
    """Response model for lead creation in HubSpot."""
    lead_id: str
    contact_id: str
    company_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class NotificationRequest(BaseModel):
    """Request model for sending notifications."""
    phone_number: str
    email: str
    appointment_datetime: datetime
    confirmation_code: str
    patient_name: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v or len(v.strip()) < 10:
            raise ValueError('Invalid phone number')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.strip().lower()


class SchedulingError(Exception):
    """Custom exception for scheduling-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SchedulingError):
    """Exception for validation errors."""
    pass


class BookingError(SchedulingError):
    """Exception for appointment booking errors."""
    pass


class CRMError(SchedulingError):
    """Exception for CRM integration errors."""
    pass


class NotificationError(SchedulingError):
    """Exception for notification sending errors."""
    pass
