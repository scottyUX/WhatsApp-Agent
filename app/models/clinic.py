from __future__ import annotations

"""
Pydantic models for clinic and package data.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OpeningHours(BaseModel):
    day: str
    hours: str


class AdditionalInfo(BaseModel):
    payments: Optional[List[Dict[str, Any]]] = None
    planning: Optional[List[Dict[str, Any]]] = None
    amenities: Optional[List[Dict[str, Any]]] = None
    accessibility: Optional[List[Dict[str, Any]]] = None


class PackageResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PackageCreateRequest(BaseModel):
    name: str = Field(..., max_length=120, description="Display name for the package")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the package inclusions"
    )
    price: Optional[Decimal] = Field(
        default=None,
        description="Optional price. Leave empty for 'contact us' style packages.",
    )
    currency: str = Field(
        default="USD", min_length=3, max_length=3, description="ISO currency code"
    )
    is_active: bool = Field(
        default=True, description="Whether the package should be suggested to patients"
    )


class PackageUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(
        default=None,
        description="Optional price. Set to null to remove pricing information.",
    )
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    is_active: Optional[bool] = None


class PackageListResponse(BaseModel):
    packages: List[PackageResponse]
    total: int


class ClinicResponse(BaseModel):
    id: uuid.UUID
    place_id: Optional[str] = None
    title: str
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country_code: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews_count: Optional[int] = Field(None, ge=0)
    categories: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    price_range: Optional[str] = None
    availability: Optional[str] = None
    country: Optional[str] = None
    package_ids: List[uuid.UUID] = Field(
        default_factory=list,
        alias="packageIds",
        description="Convenience mirror of packages linked to this clinic",
    )
    has_contract: bool = Field(
        default=False,
        alias="hasContract",
        description="Whether there is a signed agreement with this clinic",
    )
    packages: List[PackageResponse] = Field(
        default_factory=list,
        description="Expanded package metadata for frontend consumption",
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ClinicListResponse(BaseModel):
    clinics: List[ClinicResponse]
    total: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True
        populate_by_name = True


class ClinicPackageUpdateRequest(BaseModel):
    package_ids: List[uuid.UUID] = Field(
        ...,
        alias="packageIds",
        description="Full list of package identifiers that should be linked to the clinic",
    )
    has_contract: Optional[bool] = Field(
        default=None,
        alias="hasContract",
        description="Optional flag to update the contract status as part of the request",
    )

    class Config:
        populate_by_name = True


PackageResponse.model_rebuild()
PackageCreateRequest.model_rebuild()
PackageUpdateRequest.model_rebuild()
PackageListResponse.model_rebuild()
ClinicResponse.model_rebuild()
ClinicListResponse.model_rebuild()
ClinicPackageUpdateRequest.model_rebuild()
