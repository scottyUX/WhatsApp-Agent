"""
Consultant Note Router

API endpoints for consultant notes management.
"""

import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid

from app.database.db import SessionLocal
from app.database.repositories.consultant_note_repository import ConsultantNoteRepository
from app.config.rate_limits import limiter, RateLimitConfig
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/consultant-notes",
    tags=["Consultant Notes"],
)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CreateNoteRequest(BaseModel):
    patient_profile_id: str
    note_content: str
    consultation_id: Optional[str] = None
    note_type: str = "general"
    is_private: bool = False


class UpdateNoteRequest(BaseModel):
    note_content: Optional[str] = None
    note_type: Optional[str] = None
    is_private: Optional[bool] = None


class NoteResponse(BaseModel):
    id: str
    patient_profile_id: str
    consultant_email: str
    note_content: str
    consultation_id: Optional[str] = None
    note_type: str
    is_private: bool
    created_at: str
    updated_at: str


@router.post("/", response_model=NoteResponse)
@limiter.limit(RateLimitConfig.CHAT)
async def create_note(
    request: Request,
    note_data: CreateNoteRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new consultant note.
    
    Args:
        note_data: Note creation data
        
    Returns:
        Created note details
    """
    try:
        # Get consultant email from request headers or auth context
        # For now, we'll use a default consultant email
        consultant_email = "consultant@istanbulmedic.com"
        
        note_repository = ConsultantNoteRepository(db)
        note = note_repository.create(
            patient_profile_id=note_data.patient_profile_id,
            consultant_email=consultant_email,
            note_content=note_data.note_content,
            consultation_id=note_data.consultation_id,
            note_type=note_data.note_type,
            is_private=note_data.is_private
        )
        
        return NoteResponse(
            id=str(note.id),
            patient_profile_id=str(note.patient_profile_id),
            consultant_email=note.consultant_email,
            note_content=note.note_content,
            consultation_id=str(note.consultation_id) if note.consultation_id else None,
            note_type=note.note_type,
            is_private=note.is_private,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/patient/{patient_id}", response_model=List[NoteResponse])
@limiter.limit(RateLimitConfig.CHAT)
async def get_notes_by_patient(
    request: Request,
    patient_id: str,
    include_private: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all notes for a specific patient.
    
    Args:
        patient_id: Patient profile ID
        include_private: Whether to include private notes
        
    Returns:
        List of notes for the patient
    """
    try:
        note_repository = ConsultantNoteRepository(db)
        notes = note_repository.get_by_patient_profile_id(
            patient_id, 
            include_private=include_private
        )
        
        return [
            NoteResponse(
                id=str(note.id),
                patient_profile_id=str(note.patient_profile_id),
                consultant_email=note.consultant_email,
                note_content=note.note_content,
                consultation_id=str(note.consultation_id) if note.consultation_id else None,
                note_type=note.note_type,
                is_private=note.is_private,
                created_at=note.created_at.isoformat(),
                updated_at=note.updated_at.isoformat()
            )
            for note in notes
        ]
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/consultation/{consultation_id}", response_model=List[NoteResponse])
@limiter.limit(RateLimitConfig.CHAT)
async def get_notes_by_consultation(
    request: Request,
    consultation_id: str,
    include_private: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all notes for a specific consultation.
    
    Args:
        consultation_id: Consultation ID
        include_private: Whether to include private notes
        
    Returns:
        List of notes for the consultation
    """
    try:
        note_repository = ConsultantNoteRepository(db)
        notes = note_repository.get_by_consultation_id(
            consultation_id, 
            include_private=include_private
        )
        
        return [
            NoteResponse(
                id=str(note.id),
                patient_profile_id=str(note.patient_profile_id),
                consultant_email=note.consultant_email,
                note_content=note.note_content,
                consultation_id=str(note.consultation_id) if note.consultation_id else None,
                note_type=note.note_type,
                is_private=note.is_private,
                created_at=note.created_at.isoformat(),
                updated_at=note.updated_at.isoformat()
            )
            for note in notes
        ]
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put("/{note_id}", response_model=NoteResponse)
@limiter.limit(RateLimitConfig.CHAT)
async def update_note(
    request: Request,
    note_id: str,
    note_data: UpdateNoteRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing note.
    
    Args:
        note_id: Note ID
        note_data: Note update data
        
    Returns:
        Updated note details
    """
    try:
        note_repository = ConsultantNoteRepository(db)
        note = note_repository.update(
            note_id=note_id,
            note_content=note_data.note_content,
            note_type=note_data.note_type,
            is_private=note_data.is_private
        )
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail=f"Note not found: {note_id}"
            )
        
        return NoteResponse(
            id=str(note.id),
            patient_profile_id=str(note.patient_profile_id),
            consultant_email=note.consultant_email,
            note_content=note.note_content,
            consultation_id=str(note.consultation_id) if note.consultation_id else None,
            note_type=note.note_type,
            is_private=note.is_private,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.delete("/{note_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def delete_note(
    request: Request,
    note_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a note.
    
    Args:
        note_id: Note ID
        
    Returns:
        Success message
    """
    try:
        note_repository = ConsultantNoteRepository(db)
        success = note_repository.delete(note_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Note not found: {note_id}"
            )
        
        return {
            "success": True,
            "message": "Note deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for consultant notes service."""
    return {
        "status": "healthy",
        "service": "consultant_notes",
        "message": "Consultant notes service is running"
    }
