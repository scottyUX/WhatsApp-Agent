"""
Medical Data Service

Handles medical questionnaire data processing and storage.
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database.entities import User, PatientProfile, MedicalBackground
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.medical_background_repository import MedicalBackgroundRepository
from app.database.db import SessionLocal


class MedicalDataService:
    """Service for handling medical questionnaire data."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.patient_profile_repository = PatientProfileRepository(db)
        self.medical_background_repository = MedicalBackgroundRepository(db)
    
    def submit_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit medical questionnaire data.
        
        Args:
            questionnaire_data: Dictionary containing questionnaire responses
            
        Returns:
            Dictionary with submission result and patient profile info
        """
        try:
            # Extract basic info
            attendee_name = questionnaire_data.get('attendee_name', 'Unknown')
            attendee_email = questionnaire_data.get('attendee_email', 'unknown@example.com')
            booking_uid = questionnaire_data.get('booking_uid')
            
            if not booking_uid:
                raise ValueError("booking_uid is required")
            
            # Create or get user
            user = self._get_or_create_user(attendee_email, attendee_name)
            
            # Create or update patient profile
            patient_profile = self._get_or_create_patient_profile(
                user_id=user.id,
                name=attendee_name,
                email=attendee_email,
                questionnaire_data=questionnaire_data
            )
            
            # Create or update medical background
            medical_background = self._create_or_update_medical_background(
                patient_profile_id=patient_profile.id,
                questionnaire_data=questionnaire_data
            )
            
            return {
                "success": True,
                "patient_profile": {
                    "id": str(patient_profile.id),
                    "name": patient_profile.name,
                    "email": patient_profile.email,
                    "age": patient_profile.age
                },
                "medical_background": {
                    "id": str(medical_background.id),
                    "medical_data": medical_background.medical_data
                },
                "booking_uid": booking_uid
            }
            
        except Exception as e:
            print(f"Error submitting questionnaire: {e}")
            raise
    
    def get_medical_data_by_booking_uid(self, booking_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get medical data by booking UID.
        
        Args:
            booking_uid: The booking UID to search for
            
        Returns:
            Dictionary with patient profile and medical background data, or None if not found
        """
        try:
            # For now, we'll search by email since we don't have a direct booking_uid field
            # In a real implementation, you'd want to store the booking_uid in the patient profile
            # or have a separate bookings table
            
            # This is a simplified search - in production you'd want a more robust approach
            patient_profiles = self.db.query(PatientProfile).all()
            
            for profile in patient_profiles:
                # Check if this profile has medical background data
                medical_bg = self.medical_background_repository.get_by_patient_profile_id(profile.id)
                if medical_bg:
                    return {
                        "patient_profile": {
                            "id": str(profile.id),
                            "name": profile.name,
                            "email": profile.email,
                            "phone": profile.phone,
                            "age": profile.age,
                            "location": profile.location
                        },
                        "medical_background": {
                            "id": str(medical_bg.id),
                            "medical_data": medical_bg.medical_data
                        }
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting medical data: {e}")
            return None
    
    def _get_or_create_user(self, email: str, name: str) -> User:
        """Get or create user by email."""
        # Try to find user by email (assuming email is stored in phone_number field for now)
        user = self.user_repository.get_by_phone_number(email)
        
        if not user:
            # Create new user
            user = self.user_repository.create(phone_number=email, name=name)
        
        return user
    
    def _get_or_create_patient_profile(
        self, 
        user_id: uuid.UUID, 
        name: str, 
        email: str, 
        questionnaire_data: Dict[str, Any]
    ) -> PatientProfile:
        """Get or create patient profile."""
        # Try to find existing profile
        patient_profile = self.patient_profile_repository.get_by_user_id(user_id)
        
        if not patient_profile:
            # Extract additional info from questionnaire
            age_range = questionnaire_data.get('age_range', '')
            age = self._extract_age_from_range(age_range)
            
            # Create new patient profile
            patient_profile = self.patient_profile_repository.create(
                user_id=user_id,
                name=name,
                phone=email,  # Using email as phone for now
                email=email,
                age=age
            )
        else:
            # Update existing profile if needed
            age_range = questionnaire_data.get('age_range', '')
            age = self._extract_age_from_range(age_range)
            
            if age and not patient_profile.age:
                patient_profile.age = age
                self.patient_profile_repository.save(patient_profile)
        
        return patient_profile
    
    def _create_or_update_medical_background(
        self, 
        patient_profile_id: uuid.UUID, 
        questionnaire_data: Dict[str, Any]
    ) -> MedicalBackground:
        """Create or update medical background data."""
        # Check if medical background already exists
        medical_bg = self.medical_background_repository.get_by_patient_profile_id(patient_profile_id)
        
        # Prepare medical data
        medical_data = self._prepare_medical_data(questionnaire_data)
        
        if medical_bg:
            # Update existing medical background
            medical_bg.medical_data = medical_data
            self.medical_background_repository.save(medical_bg)
        else:
            # Create new medical background
            medical_bg = self.medical_background_repository.create(
                patient_profile_id=patient_profile_id,
                medical_data=medical_data
            )
        
        return medical_bg
    
    def _prepare_medical_data(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare medical data from questionnaire responses."""
        medical_data = {}
        
        # Map questionnaire fields to medical data structure
        field_mapping = {
            'age_range': 'age_range',
            'current_medications': 'current_medications',
            'current_medications_details': 'current_medications_details',
            'allergies': 'allergies',
            'allergies_details': 'allergies_details',
            'medical_conditions': 'medical_conditions',
            'medical_conditions_details': 'medical_conditions_details',
            'previous_surgeries': 'previous_surgeries',
            'previous_surgeries_details': 'previous_surgeries_details',
            'hair_loss_duration': 'hair_loss_duration',
            'hair_loss_pattern': 'hair_loss_pattern',
            'family_history': 'family_history',
            'previous_treatments': 'previous_treatments'
        }
        
        for q_field, m_field in field_mapping.items():
            if q_field in questionnaire_data and questionnaire_data[q_field] is not None:
                medical_data[m_field] = questionnaire_data[q_field]
        
        return medical_data
    
    def _extract_age_from_range(self, age_range: str) -> Optional[int]:
        """Extract numeric age from age range string."""
        if not age_range:
            return None
        
        try:
            if age_range == "65+":
                return 65
            elif "-" in age_range:
                # Extract the lower bound
                return int(age_range.split("-")[0])
            else:
                return int(age_range)
        except (ValueError, IndexError):
            return None
