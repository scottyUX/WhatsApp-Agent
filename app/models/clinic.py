from __future__ import annotations

"""
Pydantic models for clinic and package data.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    TRY = "TRY"


class OpeningHours(BaseModel):
    day: str
    hours: str


class AdditionalInfo(BaseModel):
    payments: Optional[List[Dict[str, Any]]] = None
    planning: Optional[List[Dict[str, Any]]] = None
    amenities: Optional[List[Dict[str, Any]]] = None
    accessibility: Optional[List[Dict[str, Any]]] = None


class PackageResponse(BaseModel):
    # Core Package Information
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: CurrencyEnum = Field(default=CurrencyEnum.EUR)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    clinic_id: Optional[uuid.UUID] = None

    # Treatment Specifics
    grafts_count: Optional[str] = None
    hair_transplantation_method: Optional[str] = None
    stem_cell_therapy_sessions: Optional[int] = None

    # Travel & Accommodation
    airport_lounge_access_included: Optional[bool] = None
    airport_lounge_access_details: Optional[str] = None
    breakfast_included: Optional[bool] = None
    hotel_name: Optional[str] = None
    hotel_nights_included: Optional[int] = None
    hotel_star_rating: Optional[int] = None
    private_translator_included: Optional[bool] = None
    vip_transfer_details: Optional[str] = None

    # Aftercare & Follow-ups
    aftercare_kit_supply_duration: Optional[str] = None
    laser_sessions: Optional[int] = None
    online_follow_ups_duration: Optional[str] = None
    oxygen_therapy_sessions: Optional[int] = None
    post_operation_medication_included: Optional[bool] = None
    prp_sessions_included: Optional[bool] = None
    sedation_included: Optional[bool] = None

    class Config:
        from_attributes = True


class PackageCreateRequest(BaseModel):
    # Core Package Information
    name: str = Field(..., max_length=120, description="Display name for the package")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the package inclusions"
    )
    price: Optional[Decimal] = Field(
        default=None,
        description="Optional price. Leave empty for 'contact us' style packages.",
    )
    currency: CurrencyEnum = Field(
        default=CurrencyEnum.EUR, description="Currency code (USD, EUR, GBP, TRY)"
    )
    is_active: bool = Field(
        default=True, description="Whether the package should be suggested to patients"
    )
    clinic_id: Optional[uuid.UUID] = Field(default=None, description="Clinic this package belongs to")

    # Treatment Specifics
    grafts_count: Optional[str] = Field(
        default=None, 
        description="Number of grafts (1000-6000 in 500 increments or 'Unlimited')"
    )
    hair_transplantation_method: Optional[str] = Field(
        default=None,
        description="Hair transplantation method (DHI, FUE, FUT, Sapphire FUE)"
    )
    stem_cell_therapy_sessions: Optional[int] = Field(default=0, description="Number of stem cell therapy sessions")

    # Travel & Accommodation
    airport_lounge_access_included: Optional[bool] = Field(default=False, description="Airport lounge access included")
    airport_lounge_access_details: Optional[str] = Field(default=None, description="Airport lounge access details (IST only, Both ways)")
    breakfast_included: Optional[bool] = Field(default=False, description="Breakfast included")
    hotel_name: Optional[str] = Field(default=None, description="Hotel name")
    hotel_nights_included: Optional[int] = Field(default=0, description="Number of hotel nights included")
    hotel_star_rating: Optional[int] = Field(default=0, description="Hotel star rating")
    private_translator_included: Optional[bool] = Field(default=False, description="Private translator included")
    vip_transfer_details: Optional[str] = Field(default=None, description="VIP transfer details")

    # Aftercare & Follow-ups
    aftercare_kit_supply_duration: Optional[str] = Field(default=None, description="Aftercare kit supply duration (3, 6, or 13 months)")
    laser_sessions: Optional[int] = Field(default=0, description="Number of laser sessions")
    online_follow_ups_duration: Optional[str] = Field(default=None, description="Online follow-ups duration (3, 6, 12 months, or Lifetime)")
    oxygen_therapy_sessions: Optional[int] = Field(default=0, description="Number of oxygen therapy sessions")
    post_operation_medication_included: Optional[bool] = Field(default=False, description="Post-operation medication included")
    prp_sessions_included: Optional[bool] = Field(default=False, description="PRP sessions included")
    sedation_included: Optional[bool] = Field(default=False, description="Sedation included")


class PackageUpdateRequest(BaseModel):
    # Core Package Information
    name: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(
        default=None,
        description="Optional price. Set to null to remove pricing information.",
    )
    currency: Optional[CurrencyEnum] = None
    is_active: Optional[bool] = None
    clinic_id: Optional[uuid.UUID] = None

    # Treatment Specifics
    grafts_count: Optional[str] = None
    hair_transplantation_method: Optional[str] = None
    stem_cell_therapy_sessions: Optional[int] = None

    # Travel & Accommodation
    airport_lounge_access_included: Optional[bool] = None
    airport_lounge_access_details: Optional[str] = None
    breakfast_included: Optional[bool] = None
    hotel_name: Optional[str] = None
    hotel_nights_included: Optional[int] = None
    hotel_star_rating: Optional[int] = None
    private_translator_included: Optional[bool] = None
    vip_transfer_details: Optional[str] = None

    # Aftercare & Follow-ups
    aftercare_kit_supply_duration: Optional[str] = None
    laser_sessions: Optional[int] = None
    online_follow_ups_duration: Optional[str] = None
    oxygen_therapy_sessions: Optional[int] = None
    post_operation_medication_included: Optional[bool] = None
    prp_sessions_included: Optional[bool] = None
    sedation_included: Optional[bool] = None


class PackageListResponse(BaseModel):
    packages: List[PackageResponse]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
    pages: int = Field(default=0, ge=0)


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


class ClinicUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = Field(default=None, alias="countryCode", max_length=10)
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, alias="additionalInfo")
    opening_hours: Optional[Dict[str, Any]] = Field(default=None, alias="openingHours")
    price_range: Optional[str] = Field(default=None, alias="priceRange")
    availability: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    reviews_count: Optional[int] = Field(default=None, alias="reviewsCount", ge=0)
    categories: Optional[List[str]] = None
    has_contract: Optional[bool] = Field(default=None, alias="hasContract")

    class Config:
        populate_by_name = True


PackageResponse.model_rebuild()
PackageCreateRequest.model_rebuild()
PackageUpdateRequest.model_rebuild()
PackageListResponse.model_rebuild()
ClinicResponse.model_rebuild()
ClinicListResponse.model_rebuild()
ClinicPackageUpdateRequest.model_rebuild()
ClinicUpdateRequest.model_rebuild()
