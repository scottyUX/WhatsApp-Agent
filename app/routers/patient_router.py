"""
Patient Router

API endpoints for patient data management.
"""

import traceback
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.db import SessionLocal
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.database.repositories.medical_background_repository import MedicalBackgroundRepository
from app.database.repositories.consultation_repository import ConsultationRepository
from app.database.repositories.patient_image_submission_repository import (
    PatientImageSubmissionRepository,
)
from app.database.repositories.clinic_repository import ClinicRepository
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


def _build_patient_detail_data(db: Session, patient_id: str) -> dict:
    """Return the detailed patient payload used by the patient detail endpoint."""
    patient_repository = PatientProfileRepository(db)
    medical_repository = MedicalBackgroundRepository(db)
    consultation_repository = ConsultationRepository(db)

    patient = patient_repository.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient not found: {patient_id}")

    medical_background = medical_repository.get_by_patient_profile_id(patient_id)
    consultations = consultation_repository.get_by_patient_profile_id(patient_id)

    latest_consultation = None
    if consultations:
        sorted_consultations = sorted(
            [c for c in consultations if c.start_time],
            key=lambda x: x.start_time,
            reverse=True,
        )
        latest_consultation = sorted_consultations[0] if sorted_consultations else None

    medical_summary = {
        "medications": "none",
        "medicationsDetails": "",
        "allergies": "none",
        "allergiesDetails": "",
        "medicalConditions": "none",
        "medicalConditionsDetails": "",
        "previousSurgeries": "none",
        "previousSurgeriesDetails": "",
    }

    if medical_background and medical_background.medical_data:
        medical_data = medical_background.medical_data
        medical_summary = {
            "medications": medical_data.get("current_medications", "none"),
            "medicationsDetails": medical_data.get("current_medications_details", ""),
            "allergies": medical_data.get("allergies", "none"),
            "allergiesDetails": medical_data.get("allergies_details", ""),
            "medicalConditions": medical_data.get("medical_conditions", "none"),
            "medicalConditionsDetails": medical_data.get(
                "medical_conditions_details", ""
            ),
            "previousSurgeries": medical_data.get("previous_surgeries", "none"),
            "previousSurgeriesDetails": medical_data.get(
                "previous_surgeries_details", ""
            ),
        }

    hair_loss_profile = {
        "duration": "",
        "pattern": [],
        "familyHistory": [],
        "previousTreatments": [],
    }

    if medical_background and medical_background.medical_data:
        medical_data = medical_background.medical_data
        hair_loss_profile = {
            "duration": medical_data.get("hair_loss_duration", ""),
            "pattern": medical_data.get("hair_loss_pattern", []),
            "familyHistory": medical_data.get("family_history", []),
            "previousTreatments": medical_data.get("previous_treatments", []),
        }

    consultation_status = {
        "bookingUid": "",
        "scheduledAt": "",
        "status": "none",
    }

    if latest_consultation:
        consultation_status = {
            "bookingUid": latest_consultation.zoom_meeting_id or "",
            "scheduledAt": latest_consultation.start_time.isoformat()
            if latest_consultation.start_time
            else "",
            "status": latest_consultation.status or "scheduled",
        }

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
        "location": patient.location,
        "clinicOffers": [
            str(clinic_id) for clinic_id in (patient.clinic_offer_ids or [])
        ],
        "medicalSummary": medical_summary,
        "hairLossProfile": hair_loss_profile,
        "consultationStatus": consultation_status,
        "journeyStage": journey_stage,
        "lastUpdated": patient.updated_at.isoformat(),
        "created_at": patient.created_at.isoformat(),
    }

    return result


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
                "clinicOffers": [str(clinic_id) for clinic_id in (patient.clinic_offer_ids or [])],
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


@router.get("/with-uploaded-images")
@limiter.limit(RateLimitConfig.CHAT)
async def get_patients_with_uploaded_images(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Return patient details for profiles that have uploaded images.
    Only patients with at least one image submission are included.
    """
    try:
        _ = request  # required for rate limiter to validate the endpoint signature
        image_repository = PatientImageSubmissionRepository(db)

        patient_ids = image_repository.list_patient_ids_with_images()
        if not patient_ids:
            return {"success": True, "data": [], "count": 0}

        results = []
        for patient_id in patient_ids:
            try:
                patient_data = _build_patient_detail_data(db, str(patient_id))
            except HTTPException:
                # Skip orphaned image submissions if the patient profile is missing.
                continue

            submissions = image_repository.list_by_patient_profile(patient_id)
            uploaded_images = sorted(
                {
                    url
                    for submission in submissions
                    for url in (submission.image_urls or [])
                }
            )
            patient_data["uploaded_images"] = uploaded_images
            results.append(patient_data)

        return {"success": True, "data": results, "count": len(results)}

    except HTTPException:
        raise
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
        _ = request  # required for rate limiter to validate the endpoint signature
        result = _build_patient_detail_data(db, patient_id)
        return {"success": True, "data": result}
    
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


# Pydantic models for patient updates
class MedicalSummaryUpdate(BaseModel):
    medications: str
    medicationsDetails: str
    allergies: str
    allergiesDetails: str
    medicalConditions: str
    medicalConditionsDetails: str
    previousSurgeries: str
    previousSurgeriesDetails: str

class HairLossProfileUpdate(BaseModel):
    duration: str
    pattern: List[str]
    familyHistory: List[str]
    previousTreatments: List[str]

class PatientOffersRequest(BaseModel):
    clinic_ids: List[uuid.UUID] = Field(..., alias="clinicIds")

    class Config:
        allow_population_by_field_name = True

class PatientProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    ageRange: Optional[str] = None  # Will be converted to age integer
    journeyStage: Optional[str] = None
    medicalSummary: Optional[MedicalSummaryUpdate] = None
    hairLossProfile: Optional[HairLossProfileUpdate] = None


@router.put("/{patient_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def update_patient_profile(
    request: Request,
    patient_id: str,
    update_data: PatientProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update patient profile information.
    
    Args:
        patient_id: The patient profile ID
        update_data: Updated patient data
        
    Returns:
        Updated patient profile data
    """
    try:
        patient_repository = PatientProfileRepository(db)
        medical_repository = MedicalBackgroundRepository(db)
        
        # Get existing patient
        patient = patient_repository.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient not found: {patient_id}"
            )
        
        # Update basic patient profile fields
        if update_data.name is not None:
            patient.name = update_data.name
        if update_data.email is not None:
            patient.email = update_data.email
        if update_data.phone is not None:
            patient.phone = update_data.phone
        if update_data.ageRange is not None:
            # Convert age range to age (take the lower bound)
            try:
                age_str = update_data.ageRange.split('-')[0]
                patient.age = int(age_str)
            except (ValueError, IndexError):
                # If parsing fails, keep existing age
                pass
        
        # Save patient profile changes
        patient_repository.save(patient)
        
        # Update medical background if provided
        if update_data.medicalSummary or update_data.hairLossProfile:
            # Get or create medical background
            medical_background = medical_repository.get_by_patient_profile_id(patient_id)
            if not medical_background:
                medical_background = medical_repository.create(
                    patient_profile_id=patient_id,
                    medical_data={}
                )
            
            # Update medical data
            medical_data = medical_background.medical_data or {}
            
            if update_data.medicalSummary:
                # Only update fields that are provided (not None)
                if update_data.medicalSummary.medications is not None:
                    medical_data["current_medications"] = update_data.medicalSummary.medications
                if update_data.medicalSummary.medicationsDetails is not None:
                    medical_data["current_medications_details"] = update_data.medicalSummary.medicationsDetails
                if update_data.medicalSummary.allergies is not None:
                    medical_data["allergies"] = update_data.medicalSummary.allergies
                if update_data.medicalSummary.allergiesDetails is not None:
                    medical_data["allergies_details"] = update_data.medicalSummary.allergiesDetails
                if update_data.medicalSummary.medicalConditions is not None:
                    medical_data["medical_conditions"] = update_data.medicalSummary.medicalConditions
                if update_data.medicalSummary.medicalConditionsDetails is not None:
                    medical_data["medical_conditions_details"] = update_data.medicalSummary.medicalConditionsDetails
                if update_data.medicalSummary.previousSurgeries is not None:
                    medical_data["previous_surgeries"] = update_data.medicalSummary.previousSurgeries
                if update_data.medicalSummary.previousSurgeriesDetails is not None:
                    medical_data["previous_surgeries_details"] = update_data.medicalSummary.previousSurgeriesDetails
            
            if update_data.hairLossProfile:
                # Only update fields that are provided (not None)
                if update_data.hairLossProfile.duration is not None:
                    medical_data["hair_loss_duration"] = update_data.hairLossProfile.duration
                if update_data.hairLossProfile.pattern is not None:
                    medical_data["hair_loss_pattern"] = update_data.hairLossProfile.pattern
                if update_data.hairLossProfile.familyHistory is not None:
                    medical_data["family_history"] = update_data.hairLossProfile.familyHistory
                if update_data.hairLossProfile.previousTreatments is not None:
                    medical_data["previous_treatments"] = update_data.hairLossProfile.previousTreatments
            
            medical_background.medical_data = medical_data
            medical_repository.save(medical_background)
        
        # Get updated patient data to return
        updated_patient = patient_repository.get_by_id(patient_id)
        updated_medical = medical_repository.get_by_patient_profile_id(patient_id)
        
        # Format response similar to get_patient_details
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
        
        if updated_medical and updated_medical.medical_data:
            medical_data = updated_medical.medical_data
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
        
        hair_loss_profile = {
            "duration": "",
            "pattern": [],
            "familyHistory": [],
            "previousTreatments": []
        }
        
        if updated_medical and updated_medical.medical_data:
            medical_data = updated_medical.medical_data
            hair_loss_profile = {
                "duration": medical_data.get("hair_loss_duration", ""),
                "pattern": medical_data.get("hair_loss_pattern", []),
                "familyHistory": medical_data.get("family_history", []),
                "previousTreatments": medical_data.get("previous_treatments", [])
            }
        
        result = {
            "id": str(updated_patient.id),
            "name": updated_patient.name,
            "email": updated_patient.email,
            "phone": updated_patient.phone,
            "ageRange": f"{updated_patient.age}-{updated_patient.age+10}" if updated_patient.age else None,
            "clinicOffers": [str(clinic_id) for clinic_id in (updated_patient.clinic_offer_ids or [])],
            "medicalSummary": medical_summary,
            "hairLossProfile": hair_loss_profile,
            "journeyStage": update_data.journeyStage or "discovery",
            "lastUpdated": updated_patient.updated_at.isoformat(),
            "created_at": updated_patient.created_at.isoformat()
        }
        
        return {
            "success": True,
            "data": result,
            "message": "Patient profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.post("/{patient_id}/offers")
@limiter.limit(RateLimitConfig.CHAT)
async def add_patient_offers(
    request: Request,
    patient_id: str,
    payload: PatientOffersRequest,
    db: Session = Depends(get_db)
):
    """
    Append clinic offers to a patient profile.
    """
    try:
        patient_repository = PatientProfileRepository(db)
        clinic_repository = ClinicRepository(db)

        patient = patient_repository.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient not found: {patient_id}"
            )

        clinic_ids = list(payload.clinic_ids)
        clinics = clinic_repository.get_by_ids(clinic_ids)
        found_ids = {clinic.id for clinic in clinics}
        missing_ids = sorted(
            {clinic_id for clinic_id in clinic_ids if clinic_id not in found_ids}
        )
        if missing_ids:
            missing_str = ", ".join(str(clinic_id) for clinic_id in missing_ids)
            raise HTTPException(
                status_code=404,
                detail=f"Clinics not found: {missing_str}"
            )

        updated_patient = patient_repository.add_clinic_offers(patient, clinic_ids)

        return {
            "success": True,
            "data": {
                "id": str(updated_patient.id),
                "clinicOffers": [
                    str(clinic_id) for clinic_id in (updated_patient.clinic_offer_ids or [])
                ],
            },
            "message": "Clinic offers updated successfully",
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
