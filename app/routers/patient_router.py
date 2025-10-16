"""
Patient Router

API endpoints for patient data management.
"""

import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.medical_background_repository import MedicalBackgroundRepository
from app.database.repositories.consultation_repository import ConsultationRepository
from app.config.rate_limits import limiter, RateLimitConfig
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
@limiter.limit(RateLimitConfig.CHAT)
async def get_all_patients(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get all patients with basic information for consultant interface.
    
    Returns:
        List of patients with basic info (id, name, email, phone, age)
    """
    try:
        patient_repository = PatientProfileRepository(db)
        
        # Get all patient profiles
        from app.database.entities import PatientProfile
        patients = db.query(PatientProfile).all()
        
        result = []
        for patient in patients:
            result.append({
                "id": str(patient.id),
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "age": patient.age,
                "location": patient.location,
                "created_at": patient.created_at.isoformat(),
                "updated_at": patient.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{patient_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_patient_details(
    request: Request,
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get specific patient with full medical data for consultant interface.
    
    Args:
        patient_id: The patient profile ID
        
    Returns:
        Patient details with medical background and consultation info
    """
    try:
        patient_repository = PatientProfileRepository(db)
        medical_repository = MedicalBackgroundRepository(db)
        consultation_repository = ConsultationRepository(db)
        
        # Get patient profile
        patient = patient_repository.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient not found: {patient_id}"
            )
        
        # Get medical background
        medical_background = medical_repository.get_by_patient_profile_id(patient_id)
        
        # Get consultations
        consultations = consultation_repository.get_by_patient_profile_id(patient_id)
        
        # Get latest consultation for status
        latest_consultation = None
        if consultations:
            # Sort by start_time and get the most recent
            sorted_consultations = sorted(
                [c for c in consultations if c.start_time], 
                key=lambda x: x.start_time, 
                reverse=True
            )
            latest_consultation = sorted_consultations[0] if sorted_consultations else None
        
        # Format medical summary
        medical_summary = {
            "medications": "none",
            "medicationsDetails": "",
            "allergies": "none", 
            "allergiesDetails": "",
            "medicalConditions": "none",
            "medicalConditionsDetails": "",
            "previousSurgeries": "none",
            "previousSurgeriesDetails": ""
        }
        
        if medical_background and medical_background.medical_data:
            medical_data = medical_background.medical_data
            medical_summary = {
                "medications": medical_data.get("current_medications", "none"),
                "medicationsDetails": medical_data.get("current_medications_details", ""),
                "allergies": medical_data.get("allergies", "none"),
                "allergiesDetails": medical_data.get("allergies_details", ""),
                "medicalConditions": medical_data.get("medical_conditions", "none"),
                "medicalConditionsDetails": medical_data.get("medical_conditions_details", ""),
                "previousSurgeries": medical_data.get("previous_surgeries", "none"),
                "previousSurgeriesDetails": medical_data.get("previous_surgeries_details", "")
            }
        
        # Format hair loss profile
        hair_loss_profile = {
            "duration": "",
            "pattern": [],
            "familyHistory": [],
            "previousTreatments": []
        }
        
        if medical_background and medical_background.medical_data:
            medical_data = medical_background.medical_data
            hair_loss_profile = {
                "duration": medical_data.get("hair_loss_duration", ""),
                "pattern": medical_data.get("hair_loss_pattern", []),
                "familyHistory": medical_data.get("family_history", []),
                "previousTreatments": medical_data.get("previous_treatments", [])
            }
        
        # Format consultation status
        consultation_status = {
            "bookingUid": "",
            "scheduledAt": "",
            "status": "none"
        }
        
        if latest_consultation:
            consultation_status = {
                # Use zoom_meeting_id as a stable external reference for now
                "bookingUid": latest_consultation.zoom_meeting_id or "",
                "scheduledAt": latest_consultation.start_time.isoformat() if latest_consultation.start_time else "",
                "status": latest_consultation.status or "scheduled"
            }
        
        # Determine journey stage based on consultation status
        journey_stage = "discovery"
        if latest_consultation:
            if latest_consultation.status == "scheduled":
                journey_stage = "consultation"
            elif latest_consultation.status == "completed":
                journey_stage = "recovery"
            elif latest_consultation.status == "cancelled":
                journey_stage = "discovery"
        
        result = {
            "id": str(patient.id),
            "name": patient.name,
            "email": patient.email,
            "phone": patient.phone,
            "ageRange": f"{patient.age}-{patient.age+10}" if patient.age else None,
            "medicalSummary": medical_summary,
            "hairLossProfile": hair_loss_profile,
            "consultationStatus": consultation_status,
            "journeyStage": journey_stage,
            "lastUpdated": patient.updated_at.isoformat()
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{patient_id}/medical")
@limiter.limit(RateLimitConfig.CHAT)
async def get_patient_medical_data(
    request: Request,
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get patient's medical background data.
    
    Args:
        patient_id: The patient profile ID
        
    Returns:
        Patient's medical background data
    """
    try:
        medical_repository = MedicalBackgroundRepository(db)
        
        medical_background = medical_repository.get_by_patient_profile_id(patient_id)
        if not medical_background:
            raise HTTPException(
                status_code=404,
                detail=f"Medical data not found for patient: {patient_id}"
            )
        
        return {
            "success": True,
            "data": {
                "id": str(medical_background.id),
                "patient_profile_id": str(medical_background.patient_profile_id),
                "medical_data": medical_background.medical_data,
                "created_at": medical_background.created_at.isoformat(),
                "updated_at": medical_background.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for patient service."""
    return {
        "status": "healthy",
        "service": "patients",
        "message": "Patient service is running"
    }
