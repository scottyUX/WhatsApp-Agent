"""
Package Router

Endpoints to maintain the catalog of packages that can be attached to clinics.
"""

import traceback
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.rate_limits import RateLimitConfig, limiter
from app.database.db import SessionLocal
from app.database.repositories.package_repository import PackageRepository
from app.models.clinic import (
    PackageCreateRequest,
    PackageListResponse,
    PackageResponse,
    PackageUpdateRequest,
)
from app.utils import ErrorUtils


router = APIRouter(
    prefix="/api/packages",
    tags=["Packages"],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _model_dump(payload):
    """Support both Pydantic v1 and v2."""
    if hasattr(payload, "model_dump"):
        return payload.model_dump(exclude_unset=True)
    return payload.dict(exclude_unset=True)


def _serialize_package(package) -> PackageResponse:
    return PackageResponse.model_validate(package, from_attributes=True)


@router.get("/", response_model=PackageListResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def list_packages(
    request: Request,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    """
    Return all packages. By default only active packages are returned.
    """
    try:
        repo = PackageRepository(db)
        packages = repo.list(include_inactive=include_inactive)
        payload = [_serialize_package(pkg) for pkg in packages]
        return PackageListResponse(packages=payload, total=len(payload))
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitConfig.DEFAULT)
async def create_package(
    request: Request,
    payload: PackageCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new package that can later be assigned to clinics.
    """
    try:
        repo = PackageRepository(db)
        data = _model_dump(payload)
        if "currency" in data and data["currency"]:
            data["currency"] = data["currency"].upper()
        package = repo.create(**data)
        return _serialize_package(package)
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.patch("/{package_id}", response_model=PackageResponse)
@limiter.limit(RateLimitConfig.DEFAULT)
async def update_package(
    request: Request,
    package_id: str,
    payload: PackageUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Partially update an existing package.
    """
    try:
        package_uuid = uuid.UUID(package_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package ID must be a valid UUID.",
        ) from exc

    try:
        repo = PackageRepository(db)
        package = repo.get_by_id(package_uuid)
        if package is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package not found: {package_id}",
            )

        data = _model_dump(payload)
        if "currency" in data and data["currency"]:
            data["currency"] = data["currency"].upper()

        for key, value in data.items():
            setattr(package, key, value)

        package = repo.save(package)
        return _serialize_package(package)
    except HTTPException:
        raise
    except Exception as exception:  # pragma: no cover - defensive logging
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)
