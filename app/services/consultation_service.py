"""
Consultation Service

Handles Cal.com webhook data processing and consultation management.
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.entities import Consultation, PatientProfile
from app.database.repositories.consultation_repository import ConsultationRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.db import SessionLocal


class ConsultationService:
    """Service for handling consultation data from Cal.com webhooks."""
    
    def __init__(self, db: Session):
        self.db = db
        self.consultation_repository = ConsultationRepository(db)
        self.patient_profile_repository = PatientProfileRepository(db)
    
    def process_cal_webhook(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Cal.com webhook payload and create/update consultation.
        
        Args:
            webhook_payload: Cal.com webhook payload
            
        Returns:
            Dictionary with processing result
        """
        try:
            event_type = webhook_payload.get("type", "")
            booking_data = webhook_payload.get("data", {})
            
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
        """Handle BOOKING_CREATED event."""
        cal_booking_id = booking_data.get("id")
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
        
        # Extract attendee information
        attendees = booking_data.get("attendees", [])
        attendee_name = "Unknown"
        attendee_email = ""
        attendee_timezone = None
        
        if attendees:
            attendee = attendees[0]  # Use first attendee
            attendee_name = attendee.get("name", "Unknown")
            attendee_email = attendee.get("email", "")
            attendee_timezone = attendee.get("timeZone")
        
        # Try to find existing patient profile by email
        patient_profile = self._find_patient_by_email(attendee_email)
        
        # Create consultation
        consultation = self.consultation_repository.create(
            patient_profile_id=patient_profile.id if patient_profile else None,
            zoom_meeting_id=cal_booking_id,
            topic=title,
            start_time=start_time,
            attendee_name=attendee_name,
            attendee_email=attendee_email,
            host_name="Dr. Istanbul Medic",
            host_email="doctor@istanbulmedic.com",
            raw_payload=webhook_payload,
            status=status,
            agenda=description
        )
        
        return {
            "success": True,
            "message": "Consultation created successfully",
            "consultation_id": str(consultation.id),
            "cal_booking_id": cal_booking_id,
            "action": "created",
            "patient_profile_linked": patient_profile is not None
        }
    
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
        
        return {
            "id": str(consultation.id),
            "cal_booking_id": consultation.cal_booking_id,
            "title": consultation.title,
            "description": consultation.description,
            "start_time": consultation.start_time.isoformat() if consultation.start_time else None,
            "end_time": consultation.end_time.isoformat() if consultation.end_time else None,
            "attendee_name": consultation.attendee_name,
            "attendee_email": consultation.attendee_email,
            "attendee_timezone": consultation.attendee_timezone,
            "status": consultation.status,
            "patient_profile_id": str(consultation.patient_profile_id) if consultation.patient_profile_id else None,
            "provider_id": str(consultation.provider_id) if consultation.provider_id else None,
            "procedure_id": str(consultation.procedure_id) if consultation.procedure_id else None,
            "created_at": consultation.created_at.isoformat(),
            "updated_at": consultation.updated_at.isoformat()
        }
