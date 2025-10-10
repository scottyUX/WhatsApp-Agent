"""
Medical Data Router for handling medical questionnaire API endpoints.

This router provides endpoints for:
- Submitting medical questionnaire data
- Retrieving medical data by booking UID
- Updating medical data
- Health checks for medical data services
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.db import get_db
from app.database.entities import PatientProfile, MedicalBackground
from app.services.medical_data_service import MedicalDataService
from app.models.medical_questionnaire import (
    MedicalQuestionnaireRequest,
    MedicalQuestionnaireResponse,
    MedicalDataRetrievalResponse
)

router = APIRouter(prefix="/api/medical", tags=["medical-data"])


@router.post("/questionnaire", response_model=MedicalQuestionnaireResponse)
async def submit_medical_questionnaire(
    request: MedicalQuestionnaireRequest,
    db: Session = Depends(get_db)
):
    """
    Submit medical questionnaire data.
    
    This endpoint receives medical questionnaire data from the booking confirmation page
    and stores it in the database for use during consultations.
    """
    try:
        medical_service = MedicalDataService(db)
        response = medical_service.submit_medical_questionnaire(request)
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/data/{booking_uid}", response_model=MedicalDataRetrievalResponse)
async def get_medical_data_by_booking(
    booking_uid: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve medical data by Cal.com booking UID.
    
    This endpoint allows retrieval of medical questionnaire data
    using the Cal.com booking UID as a reference.
    """
    try:
        medical_service = MedicalDataService(db)
        data = medical_service.get_medical_data_by_booking_uid(booking_uid)
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No medical data found for booking UID: {booking_uid}"
            )
        
        return MedicalDataRetrievalResponse(
            patient_profile=data.get("patient_profile"),
            medical_background=data.get("medical_background"),
            booking_info={"booking_uid": booking_uid}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def medical_data_health_check(db: Session = Depends(get_db)):
    """
    Health check for medical data services.
    
    Verifies that the medical data service can connect to the database
    and perform basic operations.
    """
    try:
        medical_service = MedicalDataService(db)
        
        # Test database connection by attempting to query
        # (This is a lightweight operation)
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "medical-data",
            "database": "connected",
            "timestamp": "2025-01-01T00:00:00Z"  # This would be actual timestamp in production
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Medical data service unhealthy: {str(e)}"
        )


@router.get("/stats")
async def get_medical_data_stats(db: Session = Depends(get_db)):
    """
    Get statistics about medical questionnaire submissions.
    
    Returns basic statistics about the number of medical questionnaires
    submitted and patient profiles created.
    """
    try:
        medical_service = MedicalDataService(db)
        
        # Get basic counts from database
        patient_count = db.query(PatientProfile).count()
        medical_background_count = db.query(MedicalBackground).count()
        
        return {
            "patient_profiles": patient_count,
            "medical_backgrounds": medical_background_count,
            "timestamp": "2025-01-01T00:00:00Z"  # This would be actual timestamp in production
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
