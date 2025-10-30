"""
Offer Router

API endpoints for offer management (CRUD operations).
"""

import math
import traceback
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.db import SessionLocal
from app.database.repositories.clinic_repository import ClinicRepository
from app.database.repositories.offer_repository import OfferRepository
from app.database.repositories.package_repository import PackageRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.config.rate_limits import RateLimitConfig, limiter
from app.models.offer import (
    OfferDeleteEnvelope,
    OfferEnvelope,
    OfferListEnvelope,
    OfferListResponse,
    OfferMutationEnvelope,
    OfferResponse,
    OfferPatientSummary,
    OfferStatusHistoryEntry,
)
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/offers",
    tags=["Offers"],
)

MAX_CLINICS_PER_OFFER = 3
MAX_PACKAGES_PER_OFFER = 3
VALID_PAYMENT_METHODS = {"credit_card", "klarna", "paypal"}
VALID_STATUSES = {
    "draft",
    "approved",
    "sent",
    "deposit_received",
    "paid_in_full",
    "refunded",
}


def _model_dump(payload):
    """Support both Pydantic v1 and v2."""
    if hasattr(payload, "model_dump"):
        return payload.model_dump(exclude_unset=True)
    return payload.dict(exclude_unset=True)


def _normalize_uuid(value: Optional[object], field_name: str) -> Optional[uuid.UUID]:
    if value is None:
        return None
    try:
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid UUID supplied for '{field_name}'.",
        ) from exc


def _normalize_uuid_list(values: Optional[List[object]], field_name: str) -> List[uuid.UUID]:
    if not values:
        return []
    result: List[uuid.UUID] = []
    for value in values:
        try:
            normalized = value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid UUID supplied in '{field_name}'.",
            ) from exc
        result.append(normalized)
    return result


def _dedupe_preserve_order(values: List[uuid.UUID]) -> List[uuid.UUID]:
    seen = set()
    deduped: List[uuid.UUID] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _normalize_payment_methods(methods: List[str]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for method in methods:
        if not isinstance(method, str):
            raise HTTPException(
                status_code=400,
                detail="Payment methods must be provided as strings.",
            )
        key = method.lower()
        if key not in VALID_PAYMENT_METHODS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment method: {method}. "
                f"Must be one of {sorted(VALID_PAYMENT_METHODS)}",
            )
        if key not in seen:
            seen.add(key)
            normalized.append(key)
    return normalized


def _validate_clinic_ids(db: Session, clinic_ids: List[uuid.UUID]) -> None:
    if not clinic_ids:
        return
    clinic_repo = ClinicRepository(db)
    clinics = clinic_repo.get_by_ids(clinic_ids)
    found_ids = {clinic.id for clinic in clinics}
    missing = [str(cid) for cid in clinic_ids if cid not in found_ids]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Clinics not found: {', '.join(missing)}",
        )


def _validate_package_ids(db: Session, package_ids: List[uuid.UUID]) -> None:
    if not package_ids:
        return
    package_repo = PackageRepository(db)
    packages = package_repo.get_by_ids(package_ids)
    found_ids = {package.id for package in packages}
    missing = [str(pid) for pid in package_ids if pid not in found_ids]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Packages not found: {', '.join(missing)}",
        )


def _serialize_status_history(history: object) -> List[OfferStatusHistoryEntry]:
    if not isinstance(history, list):
        return []

    entries: List[OfferStatusHistoryEntry] = []
    for record in history:
        if not isinstance(record, dict):
            continue

        status = record.get("status")
        if status is None:
            continue

        timestamp_value = record.get("timestamp")
        timestamp_dt: Optional[datetime] = None
        if isinstance(timestamp_value, datetime):
            timestamp_dt = timestamp_value
        elif isinstance(timestamp_value, str):
            try:
                timestamp_dt = datetime.fromisoformat(timestamp_value)
            except ValueError:
                timestamp_dt = None

        changed_value = record.get("changed_by") or record.get("changedBy")
        changed_uuid = None
        if changed_value:
            try:
                changed_uuid = (
                    changed_value
                    if isinstance(changed_value, uuid.UUID)
                    else uuid.UUID(str(changed_value))
                )
            except (TypeError, ValueError):
                changed_uuid = None

        entries.append(
            OfferStatusHistoryEntry(
                status=str(status),
                timestamp=timestamp_dt,
                notes=record.get("notes"),
                changed_by=changed_uuid,
            )
        )

    return entries


def _serialize_patient_profile(offer) -> Optional[OfferPatientSummary]:
    patient = getattr(offer, "patient_profile", None)
    if not patient:
        return None

    return OfferPatientSummary(
        id=getattr(patient, "id"),
        name=getattr(patient, "name", None),
        email=getattr(patient, "email", None),
        phone=getattr(patient, "phone", None),
    )


def _serialize_offer(offer) -> OfferResponse:
    clinic_ids = _normalize_uuid_list(offer.clinic_ids or [], "clinic_ids")
    package_ids = _normalize_uuid_list(offer.package_ids or [], "package_ids")
    patient_summary = _serialize_patient_profile(offer)

    return OfferResponse(
        id=offer.id,
        patient_profile_id=offer.patient_profile_id,
        clinic_ids=clinic_ids,
        package_ids=package_ids,
        total_price=offer.total_price,
        currency=offer.currency,
        deposit_amount=offer.deposit_amount,
        offer_url=offer.offer_url,
        payment_methods=list(offer.payment_methods or []),
        status=offer.status,
        notes=offer.notes,
        status_history=_serialize_status_history(offer.status_history),
        created_by=offer.created_by,
        created_at=offer.created_at,
        updated_at=offer.updated_at,
        patient=patient_summary,
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
    package_ids: List[str] = Field(default_factory=list, description="Array of package IDs (max 3)")
    payment_methods: List[str] = Field(..., description="Payment methods: credit_card, klarna, paypal")
    offer_url: Optional[str] = Field(default=None, description="Shareable offer URL")
    status: str = Field(default="draft", description="Offer status")
    notes: Optional[str] = None
    total_price: Optional[float] = None
    currency: str = Field(default="USD")
    deposit_amount: Optional[float] = None
    created_by: Optional[str] = None


class OfferUpdateRequest(BaseModel):
    clinic_ids: Optional[List[str]] = None
    package_ids: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    total_price: Optional[float] = None
    currency: Optional[str] = None
    deposit_amount: Optional[float] = None
    offer_url: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status")
    notes: Optional[str] = None
    changed_by: Optional[str] = None


@router.get("/", response_model=OfferListEnvelope)
@limiter.limit(RateLimitConfig.CHAT)
async def get_all_offers(
    request: Request,
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    package_id: Optional[str] = None,
    clinic_id: Optional[str] = None,
    offer_id: Optional[str] = None,
    patient_profile_id: Optional[str] = None,
    patient_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of offers.

    Query params:
        page: Page number (1-indexed)
        limit: Number of offers per page (max 100)
        status: Filter by offer status
        package_id: Filter by package UUID
        clinic_id: Filter by clinic UUID
        offer_id/id: Filter by offer UUID
        patient_profile_id: Filter by patient profile UUID
        patient_name/patient: Case-insensitive partial patient name match

    Returns:
        List of offers
    """
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'limit' must be between 1 and 100.",
            )
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'page' must be at least 1.",
            )

        normalized_status = None
        if status:
            normalized_status = status.lower()
            if normalized_status not in VALID_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status supplied. Must be one of {sorted(VALID_STATUSES)}.",
                )

        offer_id_param = offer_id or request.query_params.get("id")
        patient_name_param = patient_name or request.query_params.get("patient")

        normalized_offer_id = _normalize_uuid(offer_id_param, "offer_id") if offer_id_param else None
        normalized_patient_profile_id = (
            _normalize_uuid(patient_profile_id, "patient_profile_id") if patient_profile_id else None
        )
        normalized_clinic_id = _normalize_uuid(clinic_id, "clinic_id") if clinic_id else None
        normalized_package_id = _normalize_uuid(package_id, "package_id") if package_id else None
        cleaned_patient_name = patient_name_param.strip() if patient_name_param else None

        offer_repository = OfferRepository(db)
        offers, total = offer_repository.list_paginated(
            page=page,
            limit=limit,
            status=normalized_status,
            clinic_id=normalized_clinic_id,
            package_id=normalized_package_id,
            offer_id=normalized_offer_id,
            patient_profile_id=normalized_patient_profile_id,
            patient_name=cleaned_patient_name,
        )
        
        serialized_offers = [_serialize_offer(offer) for offer in offers]
        total_pages = math.ceil(total / limit) if total else 0
        payload = OfferListResponse(
            offers=serialized_offers,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

        return OfferListEnvelope(
            success=True,
            data=payload,
            count=len(serialized_offers),
        )
        
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{offer_id}", response_model=OfferEnvelope)
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

        payload = _serialize_offer(offer)
        return OfferEnvelope(success=True, data=payload)
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.post("/", response_model=OfferMutationEnvelope, status_code=status.HTTP_201_CREATED)
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
        patient_uuid = _normalize_uuid(
            offer_data.patient_profile_id,
            "patient_profile_id",
        )
        patient_repo = PatientProfileRepository(db)
        if not patient_repo.get_by_id(patient_uuid):
            raise HTTPException(
                status_code=404,
                detail=f"Patient not found: {offer_data.patient_profile_id}",
            )

        clinic_ids = _dedupe_preserve_order(
            _normalize_uuid_list(offer_data.clinic_ids, "clinic_ids")
        )
        if len(clinic_ids) > MAX_CLINICS_PER_OFFER:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_CLINICS_PER_OFFER} clinics allowed per offer.",
            )

        package_ids = _dedupe_preserve_order(
            _normalize_uuid_list(offer_data.package_ids, "package_ids")
        )
        if len(package_ids) > MAX_PACKAGES_PER_OFFER:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_PACKAGES_PER_OFFER} packages allowed per offer.",
            )

        _validate_clinic_ids(db, clinic_ids)
        _validate_package_ids(db, package_ids)

        payment_methods = _normalize_payment_methods(offer_data.payment_methods)

        status_value = (offer_data.status or "draft").lower()
        if status_value not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{offer_data.status}'. Must be one of {sorted(VALID_STATUSES)}.",
            )

        currency_value = (offer_data.currency or "USD").upper()
        created_by_uuid = _normalize_uuid(offer_data.created_by, "created_by")

        offer_repository = OfferRepository(db)
        offer = offer_repository.create(
            patient_profile_id=patient_uuid,
            clinic_ids=clinic_ids,
            package_ids=package_ids,
            payment_methods=payment_methods,
            status=status_value,
            notes=offer_data.notes,
            total_price=offer_data.total_price,
            currency=currency_value,
            deposit_amount=offer_data.deposit_amount,
            created_by=created_by_uuid,
            offer_url=offer_data.offer_url,
        )
        payload = _serialize_offer(offer)

        return OfferMutationEnvelope(
            success=True,
            data=payload,
            message="Offer created successfully",
        )
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put("/{offer_id}", response_model=OfferMutationEnvelope)
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
        update_fields = _model_dump(offer_data)

        if "clinic_ids" in update_fields:
            clinic_values = update_fields["clinic_ids"]
            clinic_ids = (
                _dedupe_preserve_order(_normalize_uuid_list(clinic_values, "clinic_ids"))
                if clinic_values is not None
                else []
            )
            if len(clinic_ids) > MAX_CLINICS_PER_OFFER:
                raise HTTPException(
                    status_code=400,
                    detail=f"Maximum {MAX_CLINICS_PER_OFFER} clinics allowed per offer.",
                )
            _validate_clinic_ids(db, clinic_ids)
            offer.clinic_ids = clinic_ids

        if "package_ids" in update_fields:
            package_values = update_fields["package_ids"]
            package_ids = (
                _dedupe_preserve_order(_normalize_uuid_list(package_values, "package_ids"))
                if package_values is not None
                else []
            )
            if len(package_ids) > MAX_PACKAGES_PER_OFFER:
                raise HTTPException(
                    status_code=400,
                    detail=f"Maximum {MAX_PACKAGES_PER_OFFER} packages allowed per offer.",
                )
            _validate_package_ids(db, package_ids)
            offer.package_ids = package_ids

        if "payment_methods" in update_fields:
            payment_values = update_fields["payment_methods"]
            payment_methods = (
                _normalize_payment_methods(payment_values) if payment_values is not None else []
            )
            offer.payment_methods = payment_methods

        if "status" in update_fields:
            status_value = (update_fields["status"] or "").lower()
            if status_value and status_value not in VALID_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status '{update_fields['status']}'. Must be one of {sorted(VALID_STATUSES)}.",
                )
            if status_value:
                offer.status = status_value

        if "notes" in update_fields:
            offer.notes = update_fields["notes"]

        if "total_price" in update_fields:
            offer.total_price = update_fields["total_price"]

        if "deposit_amount" in update_fields:
            offer.deposit_amount = update_fields["deposit_amount"]

        if "offer_url" in update_fields:
            offer.offer_url = update_fields["offer_url"]

        if "currency" in update_fields:
            currency_value = update_fields["currency"]
            if currency_value is None:
                raise HTTPException(
                    status_code=400,
                    detail="Currency cannot be null.",
                )
            offer.currency = str(currency_value).upper()

        updated_offer = offer_repository.save(offer)
        payload = _serialize_offer(updated_offer)
        
        return OfferMutationEnvelope(
            success=True,
            data=payload,
            message="Offer updated successfully",
        )
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put(
    "/{offer_id}/status",
    response_model=OfferMutationEnvelope,
)
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

        new_status = status_data.status.lower()
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status_data.status}'. Must be one of {sorted(VALID_STATUSES)}.",
            )
        changed_by_uuid = _normalize_uuid(status_data.changed_by, "changed_by")
        
        offer = offer_repository.update_status(
            offer_id=offer_id,
            new_status=new_status,
            notes=status_data.notes,
            changed_by=changed_by_uuid,
        )
        
        if not offer:
            raise HTTPException(
                status_code=404,
                detail=f"Offer not found: {offer_id}"
            )
        payload = _serialize_offer(offer)

        return OfferMutationEnvelope(
            success=True,
            data=payload,
            message="Offer status updated successfully",
        )
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.delete("/{offer_id}", response_model=OfferDeleteEnvelope)
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
        
        return OfferDeleteEnvelope(success=True, message="Offer deleted successfully")
        
    except HTTPException:
        raise
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)
