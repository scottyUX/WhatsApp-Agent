"""
Medical Data Service for managing patient medical questionnaire data.

This service handles the business logic for:
- Creating and updating patient profiles
- Storing medical questionnaire responses
- Retrieving medical data for consultations
- Data validation and sanitization
"""

import uuid
import json
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.entities import User, PatientProfile, MedicalBackground
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.medical_background_repository import MedicalBackgroundRepository
from app.models.medical_questionnaire import MedicalQuestionnaireRequest, MedicalQuestionnaireResponse
from app.models.enums import Gender


class MedicalDataService:
    """Service for managing medical questionnaire data."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.patient_profile_repository = PatientProfileRepository(db)
        self.medical_background_repository = MedicalBackgroundRepository(db)
    
    def submit_medical_questionnaire(
        self, 
        request: MedicalQuestionnaireRequest,
        client_meta: Optional[Dict[str, Any]] = None
    ) -> MedicalQuestionnaireResponse:
        """
        Submit medical questionnaire data and create/update patient records.
        
        Args:
            request: Medical questionnaire data
            
        Returns:
            MedicalQuestionnaireResponse with operation results
        """
        try:
            # Validate required fields
            if not request.booking_uid or not request.attendee_name or not request.attendee_email:
                return MedicalQuestionnaireResponse(
                    success=False,
                    message="Missing required fields: booking_uid, attendee_name, and attendee_email are required",
                    patient_profile_id=None,
                    medical_background_id=None,
                    created_at=datetime.utcnow()
                )
            
            # Extract booking information
            booking_uid = request.booking_uid
            attendee_name = request.attendee_name
            attendee_email = request.attendee_email
            
            # Create or get user (using email as unique identifier for chat users)
            user = self._get_or_create_user(attendee_email, attendee_name)
            
            # Create or update patient profile
            patient_profile = self._get_or_create_patient_profile(
                user_id=user.id,
                name=attendee_name,
                email=attendee_email,
                age=self._extract_age_from_range(request.age_range),
                booking_uid=booking_uid
            )
            
            # Create or update medical background
            medical_background = self._create_or_update_medical_background(
                patient_profile_id=patient_profile.id,
                request=request
            )
            
            # Track the submission
            self._track_medical_questionnaire_submission(
                booking_uid=booking_uid,
                patient_profile_id=patient_profile.id,
                submission_data={**request.dict(), **({"client_meta": client_meta} if client_meta else {})}
            )
            
            return MedicalQuestionnaireResponse(
                success=True,
                message="Medical questionnaire submitted successfully",
                patient_profile_id=str(patient_profile.id),
                medical_background_id=str(medical_background.id),
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            return MedicalQuestionnaireResponse(
                success=False,
                message=f"Failed to submit medical questionnaire: {str(e)}",
                patient_profile_id=None,
                medical_background_id=None,
                created_at=datetime.utcnow()
            )
    
    def get_medical_data_by_booking_uid(self, booking_uid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve medical data by Cal.com booking UID.
        
        Args:
            booking_uid: Cal.com booking UID
            
        Returns:
            Dictionary containing patient profile and medical background data
        """
        try:
            # Find patient profile by booking UID (stored in location field)
            patient_profile = self.db.query(PatientProfile).filter(
                PatientProfile.location == f"booking_{booking_uid}"
            ).first()
            
            if not patient_profile:
                return None
            
            # Get medical background
            medical_background = self.medical_background_repository.get_by_patient_profile_id(
                patient_profile.id
            )
            
            return {
                "patient_profile": {
                    "id": str(patient_profile.id),
                    "name": patient_profile.name,
                    "email": patient_profile.email,
                    "phone": patient_profile.phone,
                    "age": patient_profile.age,
                    "gender": patient_profile.gender.value if patient_profile.gender else None,
                    "location": patient_profile.location,
                    "created_at": patient_profile.created_at.isoformat() if patient_profile.created_at else None
                },
                "medical_background": {
                    "id": str(medical_background.id),
                    "medical_data": medical_background.medical_data,
                    "created_at": medical_background.created_at.isoformat() if medical_background.created_at else None
                } if medical_background else None
            }
            
        except Exception as e:
            print(f"Error retrieving medical data: {e}")
            return None
    
    def _get_or_create_user(self, email: str, name: str) -> User:
        """Get or create user by email."""
        # For medical questionnaire users, we use email as the phone_number field
        # with a special prefix to distinguish from WhatsApp users
        chat_phone = f"medical_{email}"
        
        user = self.user_repository.get_by_phone_number(chat_phone)
        if not user:
            user = self.user_repository.create(phone_number=chat_phone, name=name, email=email)
            # Set user type for medical questionnaire users
            user.user_type = "medical_questionnaire"
            self.db.commit()
        
        return user
    
    def _get_or_create_patient_profile(
        self, 
        user_id: uuid.UUID, 
        name: str, 
        email: str,
        age: Optional[int] = None,
        booking_uid: Optional[str] = None
    ) -> PatientProfile:
        """Get or create patient profile."""
        patient_profile = self.patient_profile_repository.get_by_user_id(user_id)
        
        if not patient_profile:
            # Create new patient profile with required fields
            patient_profile = self.patient_profile_repository.create(
                user_id=user_id,
                name=name or "Unknown",  # Ensure name is not empty
                phone=email,  # Using email as phone for medical questionnaire users
                email=email,
                location="",  # Will be set to booking_uid below
                age=age
            )
        
        # Update profile with booking information
        if booking_uid:
            patient_profile.location = f"booking_{booking_uid}"
        patient_profile.age = age or patient_profile.age
        
        # Ensure required fields are not empty
        if not patient_profile.name:
            patient_profile.name = name or "Unknown"
        if not patient_profile.phone:
            patient_profile.phone = email
        if not patient_profile.email:
            patient_profile.email = email
            
        self.patient_profile_repository.save(patient_profile)
        
        return patient_profile
    
    def _create_or_update_medical_background(
        self, 
        patient_profile_id: uuid.UUID, 
        request: MedicalQuestionnaireRequest
    ) -> MedicalBackground:
        """Create or update medical background data."""
        medical_background = self.medical_background_repository.get_by_patient_profile_id(patient_profile_id)
        
        # Prepare medical data dictionary
        medical_data = {
            "age_range": request.age_range,
            "current_medications": {
                "status": request.current_medications,
                "details": request.current_medications_details
            },
            "allergies": {
                "status": request.allergies,
                "details": request.allergies_details
            },
            "medical_conditions": {
                "status": request.medical_conditions,
                "details": request.medical_conditions_details
            },
            "previous_surgeries": {
                "status": request.previous_surgeries,
                "details": request.previous_surgeries_details
            },
            "hair_loss_duration": request.hair_loss_duration,
            "hair_loss_pattern": request.hair_loss_pattern,
            "family_history": request.family_history,
            "previous_treatments": request.previous_treatments,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        if not medical_background:
            # Create new medical background
            medical_background = self.medical_background_repository.create(
                patient_profile_id=patient_profile_id,
                medical_data=medical_data
            )
        else:
            # Update existing medical background
            medical_background.medical_data = medical_data
            self.medical_background_repository.save(medical_background)
        
        return medical_background
    
    def _extract_age_from_range(self, age_range: Optional[str]) -> Optional[int]:
        """Extract approximate age from age range selection."""
        if not age_range:
            return None
        
        age_mapping = {
            "18-25": 22,
            "26-35": 30,
            "36-45": 40,
            "46-55": 50,
            "56-65": 60,
            "65+": 70
        }
        
        return age_mapping.get(age_range)
    
    def _track_medical_questionnaire_submission(
        self, 
        booking_uid: str, 
        patient_profile_id: uuid.UUID, 
        submission_data: dict
    ) -> None:
        """Track medical questionnaire submission for analytics and audit."""
        try:
            # Check if submission already exists
            existing_submission = self.db.execute(
                "SELECT id FROM medical_questionnaire_submissions WHERE booking_uid = :booking_uid",
                {"booking_uid": booking_uid}
            ).fetchone()
            
            if not existing_submission:
                # Create new submission record
                self.db.execute(
                    """
                    INSERT INTO medical_questionnaire_submissions 
                    (booking_uid, patient_profile_id, submission_data, status)
                    VALUES (:booking_uid, :patient_profile_id, :submission_data, 'submitted')
                    """,
                    {
                        "booking_uid": booking_uid,
                        "patient_profile_id": patient_profile_id,
                        "submission_data": json.dumps(submission_data)
                    }
                )
                self.db.commit()
        except Exception as e:
            print(f"Error tracking medical questionnaire submission: {e}")
            # Don't fail the main operation if tracking fails
