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
