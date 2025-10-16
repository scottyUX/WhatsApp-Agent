"""
Pydantic models for clinic data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class OpeningHours(BaseModel):
    day: str
    hours: str


class AdditionalInfo(BaseModel):
    payments: Optional[List[Dict[str, Any]]] = None
    planning: Optional[List[Dict[str, Any]]] = None
    amenities: Optional[List[Dict[str, Any]]] = None
    accessibility: Optional[List[Dict[str, Any]]] = None


class ClinicResponse(BaseModel):
    id: str
    place_id: str
    title: str
    city: Optional[str] = None
    state: Optional[str] = None
    country_code: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    categories: List[str] = []
    image_url: Optional[str] = None
    opening_hours: List[OpeningHours] = []
    additional_info: Optional[AdditionalInfo] = None
    inserted_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClinicListResponse(BaseModel):
    clinics: List[ClinicResponse]
    total: int
    page: int
    limit: int
    total_pages: int

    class Config:
        from_attributes = True

