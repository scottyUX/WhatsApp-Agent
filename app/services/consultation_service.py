"""
Consultation Service

Handles Cal.com webhook data processing and consultation management.
"""

import uuid
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.entities import Consultation, PatientProfile, User
from app.database.repositories.consultation_repository import ConsultationRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.user_repository import UserRepository
from app.database.db import SessionLocal


class ConsultationService:
    """Service for handling consultation data from Cal.com webhooks."""
    
    def __init__(self, db: Session):
        self.db = db
        self.consultation_repository = ConsultationRepository(db)
        self.patient_profile_repository = PatientProfileRepository(db)
        self.user_repository = UserRepository(db)
    
    def process_cal_webhook(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Cal.com webhook payload and create/update consultation.
        
        Args:
            webhook_payload: Cal.com webhook payload
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Handle real Cal.com webhook structure
            event_type = webhook_payload.get("triggerEvent", webhook_payload.get("type", ""))
            booking_data = webhook_payload.get("payload", webhook_payload.get("data", {}))
            
            print(f"🔍 DEBUG: Event type: '{event_type}'")
            print(f"🔍 DEBUG: Booking data keys: {list(booking_data.keys())}")
            
            if event_type == "BOOKING_CREATED":
                return self._handle_consultation_created(booking_data, webhook_payload)
            elif event_type == "BOOKING_CANCELLED":
                return self._handle_consultation_cancelled(booking_data)
            elif event_type == "BOOKING_RESCHEDULED":
                return self._handle_consultation_rescheduled(booking_data)
            else:
                return {
                    "success": True,
                    "message": f"Unhandled event type: {event_type}",
                    "event_type": event_type
                }
                
        except Exception as e:
            print(f"Error processing Cal.com webhook: {e}")
            raise
    
    def _handle_consultation_created(self, booking_data: Dict[str, Any], webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle BOOKING_CREATED event with transaction-based error handling.
        
        Ensures that each Cal.com booking creates a complete data model:
        - User record (from attendee email/phone)
        - PatientProfile record (with attendee details)  
        - Consultation record (linked to patient profile)
        """
        cal_booking_id = booking_data.get("uid", booking_data.get("id"))
        if not cal_booking_id:
            raise ValueError("Missing booking ID in webhook payload")
        
        # Check if consultation already exists by zoom_meeting_id
        from app.database.entities import Consultation
        existing_consultations = self.db.query(Consultation).filter(
            Consultation.zoom_meeting_id == cal_booking_id
        ).all()
        if existing_consultations:
            existing_consultation = existing_consultations[0]
            return {
                "success": True,
                "message": "Consultation already exists",
                "consultation_id": str(existing_consultation.id),
                "action": "skipped"
            }
        
        # Start transaction for atomic operations
        try:
            # Extract booking details
            title = booking_data.get("title", "Consultation")
            description = booking_data.get("description")
            start_time_str = booking_data.get("startTime")
            end_time_str = booking_data.get("endTime")
            status = booking_data.get("status", "scheduled")
            
            # Parse datetime strings
            start_time = None
            end_time = None
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            
            # Extract attendee information from real Cal.com payload structure
            attendees = booking_data.get("attendees", [])
            attendee_name = "Unknown"
            attendee_email = ""
            attendee_timezone = None
            attendee_phone = None
            attendee_location = None
            
            print(f"🔍 DEBUG: Booking data keys: {list(booking_data.keys())}")
            print(f"🔍 DEBUG: Attendees: {attendees}")
            
            if attendees:
                attendee = attendees[0]  # Use first attendee
                attendee_name = attendee.get("name", "Unknown")
                attendee_email = attendee.get("email", "")
                attendee_timezone = attendee.get("timeZone")
                
                print(f"🔍 DEBUG: Extracted name: '{attendee_name}'")
                print(f"🔍 DEBUG: Extracted email: '{attendee_email}'")
            
            # Extract phone number from responses (real Cal.com structure)
            attendee_phone = self._extract_phone_from_responses(booking_data)
            print(f"🔍 DEBUG: Extracted phone: '{attendee_phone}'")
            
            # Extract location from responses
            attendee_location = self._extract_location_from_responses(booking_data)
            print(f"🔍 DEBUG: Extracted location: '{attendee_location}'")
            
            # Create or find user and patient profile (with transaction handling)
            user, patient_profile = self._create_or_find_user_and_patient(
                attendee_name=attendee_name,
                attendee_email=attendee_email,
                attendee_phone=attendee_phone,
                attendee_location=attendee_location,
                cal_booking_id=cal_booking_id
            )
            
            # Create consultation
            consultation = self.consultation_repository.create(
                patient_profile_id=patient_profile.id if patient_profile else None,
                zoom_meeting_id=cal_booking_id,
                topic=title,
                start_time=start_time,
                attendee_name=attendee_name,
                attendee_email=attendee_email,
                attendee_phone=attendee_phone,
                host_name="Dr. Istanbul Medic",
                host_email="doctor@istanbulmedic.com",
                raw_payload=webhook_payload,
                status=status,
                agenda=description
            )
            
            # Commit transaction
            self.db.commit()
            
            return {
                "success": True,
                "message": "Consultation created successfully",
                "consultation_id": str(consultation.id),
                "cal_booking_id": cal_booking_id,
                "action": "created",
                "patient_profile_linked": patient_profile is not None,
                "user_created": user is not None,
                "patient_profile_created": patient_profile is not None,
                "attendee_phone_captured": attendee_phone is not None,
                "attendee_location_captured": attendee_location is not None
            }
            
        except SQLAlchemyError as e:
            # Rollback transaction on database error
            self.db.rollback()
            print(f"❌ Database error in consultation creation: {e}")
            raise
        except Exception as e:
            # Rollback transaction on any other error
            self.db.rollback()
            print(f"❌ Unexpected error in consultation creation: {e}")
            raise
    
    def _handle_consultation_cancelled(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BOOKING_CANCELLED event."""
        cal_booking_id = booking_data.get("id")
        if not cal_booking_id:
            raise ValueError("Missing booking ID in cancellation payload")
        
        # Update consultation status to cancelled
        consultation = self.consultation_repository.update_status(cal_booking_id, "cancelled")
        
        if consultation:
            return {
                "success": True,
                "message": "Consultation cancelled successfully",
                "consultation_id": str(consultation.id),
                "cal_booking_id": cal_booking_id,
                "action": "cancelled"
            }
        else:
            return {
                "success": False,
                "message": "Consultation not found",
                "cal_booking_id": cal_booking_id,
                "action": "not_found"
            }
    
    def _handle_consultation_rescheduled(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BOOKING_RESCHEDULED event."""
        cal_booking_id = booking_data.get("id")
        if not cal_booking_id:
            raise ValueError("Missing booking ID in reschedule payload")
        
        # Find existing consultation
        consultation = self.consultation_repository.get_by_cal_booking_id(cal_booking_id)
        if not consultation:
            return {
                "success": False,
                "message": "Consultation not found for reschedule",
                "cal_booking_id": cal_booking_id,
                "action": "not_found"
            }
        
        # Update consultation times
        start_time_str = booking_data.get("startTime")
        end_time_str = booking_data.get("endTime")
        
        if start_time_str and end_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            
            consultation.start_time = start_time
            consultation.end_time = end_time
            consultation.status = "scheduled"  # Reset to scheduled after reschedule
            
            self.consultation_repository.save(consultation)
        
        return {
            "success": True,
            "message": "Consultation rescheduled successfully",
            "consultation_id": str(consultation.id),
            "cal_booking_id": cal_booking_id,
            "action": "rescheduled"
        }
    
    def _find_patient_by_email(self, email: str) -> Optional[PatientProfile]:
        """Find patient profile by email address."""
        if not email:
            return None
        
        # Search for patient profile with matching email
        patient_profiles = self.db.query(PatientProfile).filter(
            PatientProfile.email == email
        ).all()
        
        return patient_profiles[0] if patient_profiles else None
    
    def get_todays_consultations(self) -> List[Dict[str, Any]]:
        """Get today's consultations formatted for consultant interface."""
        try:
            consultations = self.consultation_repository.get_todays_consultations()
            
            result = []
            for consultation in consultations:
                result.append({
                    "id": str(consultation.id),
                    "zoom_meeting_id": consultation.zoom_meeting_id,
                    "topic": consultation.topic,
                    "agenda": consultation.agenda,
                    "start_time": consultation.start_time.isoformat() if consultation.start_time else None,
                    "duration": consultation.duration,
                    "timezone": consultation.timezone,
                    "attendee_name": consultation.attendee_name,
                    "attendee_email": consultation.attendee_email,
                    "attendee_phone": consultation.attendee_phone,
                    "status": consultation.status,
                    "host_name": consultation.host_name,
                    "host_email": consultation.host_email,
                    "patient_profile_id": str(consultation.patient_profile_id) if consultation.patient_profile_id else None
                })
            
            return result
        except Exception as e:
            # If the consultations table doesn't exist, return empty list
            print(f"Warning: Could not fetch consultations: {e}")
            return []
    
    def get_consultation_by_cal_id(self, cal_booking_id: str) -> Optional[Dict[str, Any]]:
        """Get consultation by Cal.com booking ID."""
        consultation = self.consultation_repository.get_by_cal_booking_id(cal_booking_id)
        
        if not consultation:
            return None
        
        # Calculate end_time from start_time + duration if not set
        end_time = consultation.end_time
        if not end_time and consultation.start_time and consultation.duration:
            from datetime import timedelta
            end_time = consultation.start_time + timedelta(minutes=consultation.duration)
        
        return {
            "id": str(consultation.id),
            "cal_booking_id": cal_booking_id,  # Use the searched ID
            "title": consultation.topic,  # Use topic as title
            "description": consultation.agenda,  # Use agenda as description
            "start_time": consultation.start_time.isoformat() if consultation.start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "attendee_name": consultation.attendee_name,
            "attendee_email": consultation.attendee_email,
            "attendee_timezone": consultation.timezone,
            "status": consultation.status,
            "patient_profile_id": str(consultation.patient_profile_id) if consultation.patient_profile_id else None,
            "provider_id": str(consultation.provider_id) if consultation.provider_id else None,
            "procedure_id": str(consultation.procedure_id) if consultation.procedure_id else None,
            "created_at": consultation.created_at.isoformat() if consultation.created_at else None,
            "updated_at": consultation.updated_at.isoformat() if consultation.updated_at else None
        }
    
    def _extract_phone_from_responses(self, booking_data: Dict[str, Any]) -> Optional[str]:
        """Extract phone number from Cal.com responses."""
        responses = booking_data.get("responses", {})
        
        print(f"🔍 DEBUG: Responses: {responses}")
        
        # Look for phone number in various response fields
        phone_fields = [
            "attendeePhoneNumber",
            "aiAgentCallPhoneNumber", 
            "phone",
            "phone_number",
            "phoneNumber",
            "mobile",
            "telephone"
        ]
        
        for field in phone_fields:
            if field in responses:
                phone_data = responses[field]
                print(f"🔍 DEBUG: Found phone field '{field}': {phone_data}")
                
                # Handle different response structures
                if isinstance(phone_data, dict):
                    phone = phone_data.get("value", "")
                elif isinstance(phone_data, str):
                    phone = phone_data
                else:
                    continue
                
                if phone and isinstance(phone, str):
                    cleaned_phone = phone.strip()
                    if cleaned_phone:
                        return self._normalize_phone_number(cleaned_phone)
        
        return None
    
    def _normalize_phone_number(self, phone: str) -> str:
        """
        Normalize phone number by removing punctuation and standardizing format.
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Normalized phone number string
        """
        if not phone:
            return phone
        
        # Remove all non-digit characters except + at the beginning
        normalized = re.sub(r'[^\d+]', '', phone)
        
        # If it starts with +, keep it; otherwise add + if it looks like an international number
        if not normalized.startswith('+'):
            # If it's 10 digits (US format), assume it's US
            if len(normalized) == 10:
                normalized = '+1' + normalized
            # If it's 11 digits starting with 1, assume it's US
            elif len(normalized) == 11 and normalized.startswith('1'):
                normalized = '+' + normalized
            # Otherwise, assume it needs a country code (this is a simplification)
            elif len(normalized) > 10:
                normalized = '+' + normalized
            # If it's too short or invalid, return original
            elif len(normalized) < 10:
                return phone  # Return original for invalid numbers
        
        return normalized
    
    def _extract_location_from_responses(self, booking_data: Dict[str, Any]) -> Optional[str]:
        """Extract location from Cal.com responses."""
        responses = booking_data.get("responses", {})
        
        # Look for common location field names
        location_fields = ["location", "city", "country", "address", "where_are_you_from"]
        
        for field in location_fields:
            if field in responses:
                location = responses[field]
                if location and isinstance(location, str):
                    cleaned_location = location.strip()
                    if cleaned_location:
                        return cleaned_location
        
        return None
    
    def _create_or_find_user_and_patient(
        self, 
        attendee_name: str, 
        attendee_email: str, 
        attendee_phone: Optional[str] = None,
        attendee_location: Optional[str] = None,
        cal_booking_id: Optional[str] = None
    ) -> tuple[Optional[User], Optional[PatientProfile]]:
        """
        Create or find user and patient profile for booking.
        
        Uses transaction-based error handling to ensure data consistency.
        Prioritizes phone number matching for better deduplication.
        
        Returns:
            Tuple of (user, patient_profile)
        """
        if not attendee_email:
            print(f"⚠️ No email provided for attendee: {attendee_name}")
            return None, None
        
        # Start transaction for atomic operations
        try:
            # Step 1: Find or create User (prioritize phone matching)
            user = self._find_or_create_user(attendee_name, attendee_email, attendee_phone)
            if not user:
                return None, None
            
            # Step 2: Find or create PatientProfile
            patient_profile = self._find_or_create_patient_profile(
                user, attendee_name, attendee_email, attendee_phone, attendee_location
            )
            if not patient_profile:
                # If patient profile creation fails, we still have the user
                # This is acceptable as the consultation can still be created
                print(f"⚠️ Patient profile creation failed, but user exists: {user.id}")
                return user, None
            
            # Commit transaction
            self.db.commit()
            print(f"✅ Successfully created/found user and patient profile")
            return user, patient_profile
            
        except SQLAlchemyError as e:
            # Rollback transaction on database error
            self.db.rollback()
            print(f"❌ Database error in user/patient creation: {e}")
            raise
        except Exception as e:
            # Rollback transaction on any other error
            self.db.rollback()
            print(f"❌ Unexpected error in user/patient creation: {e}")
            raise
    
    def _find_or_create_user(self, attendee_name: str, attendee_email: str, attendee_phone: Optional[str] = None) -> Optional[User]:
        """
        Find or create user with improved deduplication logic.
        
        Deduplication order:
        1. Match by normalized phone (if available)
        2. Fallback to email
        3. If both missing, treat as new lead
        """
        # Normalize phone number if available
        normalized_phone = None
        if attendee_phone:
            normalized_phone = self._normalize_phone_number(attendee_phone)
        
        # Step 1: Try to find by normalized phone number
        if normalized_phone:
            user = self.user_repository.get_by_phone_number(normalized_phone)
            if user:
                print(f"✅ Found existing user by phone: {user.id} ({normalized_phone})")
                return user
        
        # Step 2: Fallback to email lookup
        user = self.user_repository.get_by_phone_number(attendee_email)
        if user:
            print(f"✅ Found existing user by email: {user.id} ({attendee_email})")
            return user
        
        # Step 3: Create new user
        # Use normalized phone if available, otherwise fallback to email
        user_identifier = normalized_phone or attendee_email
        
        try:
            user = self.user_repository.create(
                phone_number=user_identifier,
                name=attendee_name
            )
            print(f"✅ Created new user: {user.id} ({user_identifier})")
            return user
        except Exception as e:
            print(f"❌ Failed to create user: {e}")
            return None
    
    def _find_or_create_patient_profile(
        self, 
        user: User, 
        attendee_name: str, 
        attendee_email: str, 
        attendee_phone: Optional[str] = None,
        attendee_location: Optional[str] = None
    ) -> Optional[PatientProfile]:
        """
        Find or create patient profile with improved deduplication logic.
        """
        # Step 1: Try to find by email
        patient_profile = self._find_patient_by_email(attendee_email)
        if patient_profile:
            print(f"✅ Found existing patient profile by email: {patient_profile.id}")
            return patient_profile
        
        # Step 2: Try to find by user_id
        patient_profile = self._find_patient_by_user_id(user.id)
        if patient_profile:
            print(f"✅ Found existing patient profile by user_id: {patient_profile.id}")
            return patient_profile
        
        # Step 3: Try to find by normalized phone (if available)
        if attendee_phone:
            normalized_phone = self._normalize_phone_number(attendee_phone)
            patient_profile = self._find_patient_by_phone(normalized_phone)
            if patient_profile:
                print(f"✅ Found existing patient profile by phone: {patient_profile.id}")
                return patient_profile
        
        # Step 4: Create new patient profile
        try:
            patient_profile = self.patient_profile_repository.create(
                user_id=user.id,
                name=attendee_name,
                phone=attendee_phone or attendee_email,  # Use phone if available, otherwise email
                email=attendee_email,
                location=attendee_location
            )
            print(f"✅ Created new patient profile: {patient_profile.id} ({attendee_email})")
            return patient_profile
        except Exception as e:
            print(f"❌ Failed to create patient profile: {e}")
            return None
    
    def _find_patient_by_user_id(self, user_id: uuid.UUID) -> Optional[PatientProfile]:
        """Find patient profile by user ID."""
        return self.db.query(PatientProfile).filter(
            PatientProfile.user_id == user_id
        ).first()
    
    def _find_patient_by_phone(self, phone: str) -> Optional[PatientProfile]:
        """Find patient profile by phone number."""
        return self.db.query(PatientProfile).filter(
            PatientProfile.phone == phone
        ).first()
