"""
Offer Router

API endpoints for offer management (CRUD operations).
"""

import traceback
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.db import SessionLocal
from app.database.repositories.offer_repository import OfferRepository
from app.database.repositories.clinic_repository import ClinicRepository
from app.database.repositories.package_repository import PackageRepository
from app.config.rate_limits import limiter, RateLimitConfig
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/offers",
    tags=["Offers"],
)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request/Response models
class OfferCreateRequest(BaseModel):
    patient_profile_id: str = Field(..., description="Patient profile ID")
    clinic_ids: List[str] = Field(..., description="Array of clinic IDs (max 3)")
    payment_methods: List[str] = Field(..., description="Payment methods: credit_card, klarna, paypal")
    status: str = Field(default="draft", description="Offer status")
    notes: Optional[str] = None
    total_price: Optional[float] = None
    currency: str = Field(default="USD")
    deposit_amount: Optional[float] = None
    created_by: Optional[str] = None


class OfferUpdateRequest(BaseModel):
    clinic_ids: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    total_price: Optional[float] = None
    deposit_amount: Optional[float] = None


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status")
    notes: Optional[str] = None
    changed_by: Optional[str] = None


@router.get("/")
@limiter.limit(RateLimitConfig.CHAT)
async def get_all_offers(
    request: Request,
    patient_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all offers with optional filtering.
    
    Query params:
        patient_id: Filter by patient profile ID
        status: Filter by offer status
        
    Returns:
        List of offers
    """
    try:
        offer_repository = OfferRepository(db)
        
        if patient_id:
            offers = offer_repository.get_by_patient_profile_id(patient_id)
        elif status:
            offers = offer_repository.get_by_status(status)
        else:
            offers = offer_repository.get_all(limit=100)
        
        result = []
        for offer in offers:
            result.append({
                "id": str(offer.id),
                "patient_profile_id": str(offer.patient_profile_id),
                "clinic_ids": [str(cid) for cid in offer.clinic_ids],
                "total_price": float(offer.total_price) if offer.total_price else None,
                "currency": offer.currency,
                "deposit_amount": float(offer.deposit_amount) if offer.deposit_amount else None,
                "payment_methods": offer.payment_methods,
                "status": offer.status,
                "notes": offer.notes,
                "status_history": offer.status_history,
                "created_by": str(offer.created_by) if offer.created_by else None,
                "created_at": offer.created_at.isoformat() if offer.created_at else None,
                "updated_at": offer.updated_at.isoformat() if offer.updated_at else None,
            })
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{offer_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_offer(
    request: Request,
    offer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific offer by ID.
    
    Args:
        offer_id: The offer ID
        
    Returns:
        Offer details
    """
    try:
        offer_repository = OfferRepository(db)
        offer = offer_repository.get_by_id(offer_id)
        
        if not offer:
            raise HTTPException(
                status_code=404,
                detail=f"Offer not found: {offer_id}"
            )
        
        return {
            "success": True,
            "data": {
                "id": str(offer.id),
                "patient_profile_id": str(offer.patient_profile_id),
                "clinic_ids": [str(cid) for cid in offer.clinic_ids],
                "total_price": float(offer.total_price) if offer.total_price else None,
                "currency": offer.currency,
                "deposit_amount": float(offer.deposit_amount) if offer.deposit_amount else None,
                "payment_methods": offer.payment_methods,
                "status": offer.status,
                "notes": offer.notes,
                "status_history": offer.status_history,
                "created_by": str(offer.created_by) if offer.created_by else None,
                "created_at": offer.created_at.isoformat() if offer.created_at else None,
                "updated_at": offer.updated_at.isoformat() if offer.updated_at else None,
            }
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.post("/")
@limiter.limit(RateLimitConfig.CHAT)
async def create_offer(
    request: Request,
    offer_data: OfferCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new offer.
    
    Returns:
        Created offer
    """
    try:
        # Validate clinic count (max 3)
        if len(offer_data.clinic_ids) > 3:
            raise HTTPException(
                status_code=400,
                detail="Maximum 3 clinics allowed per offer"
            )
        
        # Validate payment methods
        valid_methods = ['credit_card', 'klarna', 'paypal']
        for method in offer_data.payment_methods:
            if method not in valid_methods:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid payment method: {method}. Must be one of {valid_methods}"
                )
        
        offer_repository = OfferRepository(db)
        
        offer = offer_repository.create(
            patient_profile_id=offer_data.patient_profile_id,
            clinic_ids=offer_data.clinic_ids,
            payment_methods=offer_data.payment_methods,
            status=offer_data.status,
            notes=offer_data.notes,
            total_price=offer_data.total_price,
            currency=offer_data.currency,
            deposit_amount=offer_data.deposit_amount,
            created_by=offer_data.created_by
        )
        
        return {
            "success": True,
            "data": {
                "id": str(offer.id),
                "patient_profile_id": str(offer.patient_profile_id),
                "clinic_ids": [str(cid) for cid in offer.clinic_ids],
                "payment_methods": offer.payment_methods,
                "status": offer.status,
            },
            "message": "Offer created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put("/{offer_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def update_offer(
    request: Request,
    offer_id: str,
    offer_data: OfferUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing offer.
    
    Returns:
        Updated offer
    """
    try:
        offer_repository = OfferRepository(db)
        offer = offer_repository.get_by_id(offer_id)
        
        if not offer:
            raise HTTPException(
                status_code=404,
                detail=f"Offer not found: {offer_id}"
            )
        
        # Update fields if provided
        if offer_data.clinic_ids is not None:
            if len(offer_data.clinic_ids) > 3:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 3 clinics allowed per offer"
                )
            offer.clinic_ids = [uuid.UUID(cid) if isinstance(cid, str) else cid for cid in offer_data.clinic_ids]
        
        if offer_data.payment_methods is not None:
            valid_methods = ['credit_card', 'klarna', 'paypal']
            for method in offer_data.payment_methods:
                if method not in valid_methods:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid payment method: {method}"
                    )
            offer.payment_methods = offer_data.payment_methods
        
        if offer_data.status is not None:
            offer.status = offer_data.status
        
        if offer_data.notes is not None:
            offer.notes = offer_data.notes
        
        if offer_data.total_price is not None:
            offer.total_price = offer_data.total_price
        
        if offer_data.deposit_amount is not None:
            offer.deposit_amount = offer_data.deposit_amount
        
        updated_offer = offer_repository.save(offer)
        
        return {
            "success": True,
            "data": {
                "id": str(updated_offer.id),
                "patient_profile_id": str(updated_offer.patient_profile_id),
                "clinic_ids": [str(cid) for cid in updated_offer.clinic_ids],
                "payment_methods": updated_offer.payment_methods,
                "status": updated_offer.status,
            },
            "message": "Offer updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put("/{offer_id}/status")
@limiter.limit(RateLimitConfig.CHAT)
async def update_offer_status(
    request: Request,
    offer_id: str,
    status_data: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update offer status and add to history.
    
    Returns:
        Updated offer with status history
    """
    try:
        offer_repository = OfferRepository(db)
        
        offer = offer_repository.update_status(
            offer_id=offer_id,
            new_status=status_data.status,
            notes=status_data.notes,
            changed_by=status_data.changed_by
        )
        
        if not offer:
            raise HTTPException(
                status_code=404,
                detail=f"Offer not found: {offer_id}"
            )
        
        return {
            "success": True,
            "data": {
                "id": str(offer.id),
                "status": offer.status,
                "status_history": offer.status_history,
            },
            "message": "Offer status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.delete("/{offer_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def delete_offer(
    request: Request,
    offer_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an offer.
    
    Returns:
        Success message
    """
    try:
        offer_repository = OfferRepository(db)
        deleted = offer_repository.delete(offer_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Offer not found: {offer_id}"
            )
        
        return {
            "success": True,
            "message": "Offer deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)

