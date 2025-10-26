"""
Consultation Router

API endpoints for consultation data management.
"""

import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.services.consultation_service import ConsultationService
from app.config.rate_limits import limiter, RateLimitConfig
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/consultations",
    tags=["Consultations"],
)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/today")
@limiter.limit(RateLimitConfig.CHAT)
async def get_todays_consultations(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get today's consultations for consultant interface.
    
    Returns:
        List of today's consultations with patient information
    """
    try:
        consultation_service = ConsultationService(db)
        consultations = consultation_service.get_todays_consultations()
        
        return {
            "success": True,
            "data": consultations,
            "count": len(consultations)
        }
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/by-email/{email}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_consultation_by_email(
    request: Request,
    email: str,
    db: Session = Depends(get_db)
):
    """
    Get most recent consultation by attendee email.
    
    Args:
        email: The attendee email address (will be URL-decoded)
        
    Returns:
        Consultation details
    """
    try:
        from app.database.entities import Consultation
        from datetime import datetime
        from urllib.parse import unquote
        
        # Decode URL-encoded email (e.g., %40 -> @)
        decoded_email = unquote(email)
        
        print(f"🔍 Looking up consultation for email: {decoded_email} (original: {email})")
        
        # Find the most recent consultation for this email
        consultations = db.query(Consultation).filter(
            Consultation.attendee_email == decoded_email
        ).order_by(Consultation.created_at.desc()).all()
        
        if not consultations:
            raise HTTPException(
                status_code=404,
                detail=f"No consultation found for email: {decoded_email}"
            )
        
        consultation = consultations[0]
        
        # Calculate end_time from start_time + duration if not set
        end_time = consultation.end_time
        if not end_time and consultation.start_time and consultation.duration:
            from datetime import timedelta
            end_time = consultation.start_time + timedelta(minutes=consultation.duration)
        
        consultation_data = {
            "id": str(consultation.id),
            "cal_booking_id": consultation.zoom_meeting_id,
            "title": (consultation.topic if consultation.topic else "Consultation"),
            "description": (consultation.agenda if consultation.agenda else None),
            "start_time": consultation.start_time.isoformat() if consultation.start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "attendee_name": getattr(consultation, 'attendee_name', None) or "Unknown",
            "attendee_email": getattr(consultation, 'attendee_email', None) or decoded_email,
            "host_name": getattr(consultation, 'host_name', None) or "Istanbul Medic",
            "host_email": getattr(consultation, 'host_email', None) or "doctor@istanbulmedic.com",
            "attendee_phone": getattr(consultation, 'attendee_phone', None) or None,
            "attendee_timezone": getattr(consultation, 'timezone', None),
            "status": getattr(consultation, 'status', 'unknown'),
            "patient_profile_id": str(consultation.patient_profile_id) if consultation.patient_profile_id else None,
            "created_at": consultation.created_at.isoformat() if consultation.created_at else None,
            "updated_at": consultation.updated_at.isoformat() if consultation.updated_at else None
        }
        
        return {
            "success": True,
            "data": consultation_data
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{cal_booking_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_consultation_by_cal_id(
    request: Request,
    cal_booking_id: str,
    db: Session = Depends(get_db)
):
    """
    Get consultation by Cal.com booking ID.
    
    Args:
        cal_booking_id: The Cal.com booking ID
        
    Returns:
        Consultation details
    """
    try:
        consultation_service = ConsultationService(db)
        consultation = consultation_service.get_consultation_by_cal_id(cal_booking_id)
        
        if not consultation:
            raise HTTPException(
                status_code=404,
                detail=f"Consultation not found: {cal_booking_id}"
            )
        
        return {
            "success": True,
            "data": consultation
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for consultation service."""
    return {
        "status": "healthy",
        "service": "consultations",
        "message": "Consultation service is running"
    }
