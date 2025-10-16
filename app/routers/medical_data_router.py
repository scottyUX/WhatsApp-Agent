"""
Medical Data Router

API endpoints for medical questionnaire data handling.
"""

import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.services.medical_data_service import MedicalDataService
from app.config.rate_limits import limiter, RateLimitConfig
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/medical",
    tags=["Medical Data"],
)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/questionnaire")
@limiter.limit(RateLimitConfig.CHAT)
async def submit_questionnaire(
    request: Request,
    questionnaire_data: dict,
    db: Session = Depends(get_db)
):
    """
    Submit medical questionnaire data.
    
    Expected data structure:
    {
        "booking_uid": "string",
        "attendee_name": "string", 
        "attendee_email": "string",
        "age_range": "string",
        "current_medications": "string",
        "current_medications_details": "string",
        "allergies": "string",
        "allergies_details": "string",
        "medical_conditions": "string",
        "medical_conditions_details": "string",
        "previous_surgeries": "string",
        "previous_surgeries_details": "string",
        "hair_loss_duration": "string",
        "hair_loss_pattern": ["string"],
        "family_history": ["string"],
        "previous_treatments": ["string"]
    }
    """
    try:
        # Validate required fields
        required_fields = ["booking_uid", "attendee_name", "attendee_email"]
        for field in required_fields:
            if field not in questionnaire_data or not questionnaire_data[field]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required field: {field}"
                )
        
        # Create medical data service
        medical_service = MedicalDataService(db)
        
        # Submit questionnaire data
        result = medical_service.submit_questionnaire(questionnaire_data)
        
        return {
            "success": True,
            "message": "Medical questionnaire submitted successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/data/{booking_uid}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_medical_data(
    request: Request,
    booking_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get medical data by booking UID.
    
    Args:
        booking_uid: The booking UID to search for
        
    Returns:
        Medical data for the specified booking
    """
    try:
        # Create medical data service
        medical_service = MedicalDataService(db)
        
        # Get medical data
        medical_data = medical_service.get_medical_data_by_booking_uid(booking_uid)
        
        if not medical_data:
            raise HTTPException(
                status_code=404,
                detail=f"No medical data found for booking UID: {booking_uid}"
            )
        
        return {
            "success": True,
            "data": medical_data
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for medical data service."""
    return {
        "status": "healthy",
        "service": "medical_data",
        "message": "Medical data service is running"
    }
