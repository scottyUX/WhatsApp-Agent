"""
Pydantic models for medical questionnaire data validation and serialization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class MedicalQuestionnaireRequest(BaseModel):
    """Request model for medical questionnaire submission."""
    
    # Booking information
    booking_uid: str = Field(..., description="Cal.com booking UID")
    attendee_name: str = Field(..., description="Patient name from booking")
    attendee_email: str = Field(..., description="Patient email from booking")
    
    # Personal Information
    age_range: Optional[str] = Field(None, description="Age range selection")
    
    # Medical Background
    current_medications: Optional[str] = Field(None, description="Current medications status")
    current_medications_details: Optional[str] = Field(None, description="Details about current medications")
    allergies: Optional[str] = Field(None, description="Allergies status")
    allergies_details: Optional[str] = Field(None, description="Details about allergies")
    medical_conditions: Optional[str] = Field(None, description="Medical conditions status")
    medical_conditions_details: Optional[str] = Field(None, description="Details about medical conditions")
    previous_surgeries: Optional[str] = Field(None, description="Previous surgeries status")
    previous_surgeries_details: Optional[str] = Field(None, description="Details about previous surgeries")
    
    # Hair Loss Information
    hair_loss_duration: Optional[str] = Field(None, description="Duration of hair loss")
    hair_loss_pattern: List[str] = Field(default_factory=list, description="Hair loss patterns")
    family_history: List[str] = Field(default_factory=list, description="Family history of hair loss")
    previous_treatments: List[str] = Field(default_factory=list, description="Previous hair loss treatments")
    
    @validator('age_range')
    def validate_age_range(cls, v):
        if v and v not in ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']:
            raise ValueError('Invalid age range')
        return v
    
    @validator('current_medications', 'allergies', 'medical_conditions', 'previous_surgeries')
    def validate_yes_no_fields(cls, v):
        if v and v not in ['none', 'yes']:
            raise ValueError('Field must be "none" or "yes"')
        return v
    
    @validator('hair_loss_duration')
    def validate_hair_loss_duration(cls, v):
        if v and v not in ['less-than-1-year', '1-2-years', '2-5-years', '5-10-years', 'more-than-10-years']:
            raise ValueError('Invalid hair loss duration')
        return v


class MedicalQuestionnaireResponse(BaseModel):
    """Response model for medical questionnaire operations."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    patient_profile_id: Optional[str] = Field(None, description="Created patient profile ID")
    medical_background_id: Optional[str] = Field(None, description="Created medical background ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class MedicalDataRetrievalResponse(BaseModel):
    """Response model for retrieving medical data."""
    
    patient_profile: Optional[dict] = Field(None, description="Patient profile data")
    medical_background: Optional[dict] = Field(None, description="Medical background data")
    booking_info: Optional[dict] = Field(None, description="Associated booking information")


class MedicalDataUpdateRequest(BaseModel):
    """Request model for updating medical data."""
    
    medical_data: dict = Field(..., description="Updated medical data")
    notes: Optional[str] = Field(None, description="Additional notes about the update")
