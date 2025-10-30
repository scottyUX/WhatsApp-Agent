from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class OfferStatusHistoryEntry(BaseModel):
    status: str
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None
    changed_by: Optional[uuid.UUID] = Field(default=None, alias="changedBy")

    model_config = ConfigDict(populate_by_name=True)


class OfferPatientSummary(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class OfferResponse(BaseModel):
    id: uuid.UUID
    patient_profile_id: uuid.UUID = Field(alias="patientProfileId")
    clinic_ids: List[uuid.UUID] = Field(default_factory=list, alias="clinicIds")
    package_ids: List[uuid.UUID] = Field(default_factory=list, alias="packageIds")
    total_price: Optional[Decimal] = Field(default=None, alias="totalPrice")
    currency: str
    deposit_amount: Optional[Decimal] = Field(default=None, alias="depositAmount")
    offer_url: Optional[str] = Field(default=None, alias="offerUrl")
    payment_methods: List[str] = Field(default_factory=list, alias="paymentMethods")
    status: str
    notes: Optional[str] = None
    status_history: List[OfferStatusHistoryEntry] = Field(
        default_factory=list, alias="statusHistory"
    )
    created_by: Optional[uuid.UUID] = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    patient: Optional[OfferPatientSummary] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class OfferListResponse(BaseModel):
    offers: List[OfferResponse]
    total: int
    page: int
    page_size: int = Field(default=50, alias="pageSize")
    total_pages: int = Field(default=0, alias="totalPages")

    model_config = ConfigDict(populate_by_name=True)


class OfferEnvelope(BaseModel):
    success: bool = True
    data: OfferResponse

    model_config = ConfigDict(populate_by_name=True)


class OfferListEnvelope(BaseModel):
    success: bool = True
    data: OfferListResponse
    count: int

    model_config = ConfigDict(populate_by_name=True)


class OfferMutationEnvelope(BaseModel):
    success: bool = True
    data: OfferResponse
    message: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class OfferDeleteEnvelope(BaseModel):
    success: bool = True
    message: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
