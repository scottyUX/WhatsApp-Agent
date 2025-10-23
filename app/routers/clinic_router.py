"""
Clinic Router

Endpoints to manage clinic metadata and the packages assigned to each clinic.
"""

import math
import traceback
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.config.rate_limits import RateLimitConfig, limiter
from app.database.db import SessionLocal
from app.database.repositories.clinic_repository import ClinicRepository
from app.database.repositories.package_repository import PackageRepository
from app.models.clinic import (
    ClinicListResponse,
    ClinicPackageUpdateRequest,
    ClinicResponse,
    ClinicUpdateRequest,
    PackageResponse,
)
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/clinics",
    tags=["Clinics"],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serialize_packages(packages) -> List[PackageResponse]:
    return [
        PackageResponse.model_validate(pkg, from_attributes=True)
        for pkg in packages
    ]


def _serialize_clinic(clinic) -> ClinicResponse:
    packages = _serialize_packages(clinic.packages or [])
    # Mirror package IDs from the attached packages if they are not already hydrated
    package_ids = clinic.package_ids or [pkg.id for pkg in clinic.packages]

    return ClinicResponse.model_validate(
        clinic,
        from_attributes=True,
        update={
            "package_ids": package_ids,
            "packages": packages,
        },
    )


@router.get("/", response_model=ClinicListResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def list_clinics(
    request: Request,
    page: int = 1,
    limit: int = 20,
    has_contract: Optional[bool] = Query(
        default=None,
        alias="hasContract",
        description="Optional filter to return only clinics with/without a contract.",
    ),
    db: Session = Depends(get_db),
):
    """
    List clinics with pagination, including package metadata.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'limit' must be between 1 and 100.",
        )
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'page' must be greater than 0.",
        )

    try:
        clinic_repo = ClinicRepository(db)
        clinics, total = clinic_repo.list_paginated(
            page=page,
            limit=limit,
            has_contract=has_contract,
        )

        total_pages = math.ceil(total / limit) if total else 0
        payload = [
            _serialize_clinic(clinic)
            for clinic in clinics
        ]

        return ClinicListResponse(
            clinics=payload,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.get("/{clinic_id}", response_model=ClinicResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def get_clinic(
    request: Request,
    clinic_id: str,
    db: Session = Depends(get_db),
):
    """
    Fetch a single clinic by UUID.
    """
    try:
        clinic_uuid = uuid.UUID(clinic_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinic ID must be a valid UUID.",
        ) from exc

    try:
        clinic_repo = ClinicRepository(db)
        clinic = clinic_repo.get_by_id(clinic_uuid)
        if clinic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clinic not found: {clinic_id}",
            )
        return _serialize_clinic(clinic)
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.put("/{clinic_id}/packages", response_model=ClinicResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def update_clinic_packages(
    request: Request,
    clinic_id: str,
    payload: ClinicPackageUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Replace the list of packages assigned to a clinic.

    The request overwrites the existing assignments. Provide the full list of
    package IDs that should remain linked to the clinic.
    """
    try:
        clinic_uuid = uuid.UUID(clinic_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinic ID must be a valid UUID.",
        ) from exc

    try:
        clinic_repo = ClinicRepository(db)
        package_repo = PackageRepository(db)

        clinic = clinic_repo.get_by_id(clinic_uuid)
        if clinic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clinic not found: {clinic_id}",
            )

        package_ids = payload.package_ids
        packages = package_repo.get_by_ids(package_ids)
        missing_ids = sorted(
            {pkg_id for pkg_id in package_ids} - {pkg.id for pkg in packages}
        )
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Packages not found: {', '.join(str(mid) for mid in missing_ids)}",
            )

        clinic = clinic_repo.set_packages(
            clinic,
            packages,
            has_contract=payload.has_contract,
        )
        return _serialize_clinic(clinic)
    except HTTPException:
        raise
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.patch("/{clinic_id}", response_model=ClinicResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def update_clinic(
    request: Request,
    clinic_id: str,
    payload: ClinicUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Partially update editable clinic fields such as contact details or metadata.
    """
    try:
        clinic_uuid = uuid.UUID(clinic_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinic ID must be a valid UUID.",
        ) from exc

    try:
        clinic_repo = ClinicRepository(db)
        clinic = clinic_repo.get_by_id(clinic_uuid)
        if clinic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clinic not found: {clinic_id}",
            )

        update_data = payload.model_dump(exclude_unset=True, by_alias=False)
        allowed_fields = {
            "title",
            "location",
            "city",
            "state",
            "country",
            "country_code",
            "phone",
            "email",
            "website",
            "image_url",
            "additional_info",
            "opening_hours",
            "price_range",
            "availability",
            "rating",
            "reviews_count",
            "categories",
            "has_contract",
        }
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields supplied for update.",
            )

        clinic = clinic_repo.update_fields(clinic, filtered_data)
        return _serialize_clinic(clinic)
    except HTTPException:
        raise
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)
