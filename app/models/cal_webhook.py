from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class CalAttendee:
    name: str
    email: str
    timeZone: Optional[str] = None


@dataclass
class CalBooking:
    id: str
    title: str
    startTime: str
    endTime: str
    attendees: List[CalAttendee]
    status: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CalWebhookPayload:
    type: str  # BOOKING_CREATED, BOOKING_CANCELLED, etc.
    data: CalBooking
    created_at: Optional[str] = None
    trigger: Optional[str] = None


@dataclass
class CalWebhookResponse:
    status: str
    message: str
    booking_id: Optional[str] = None
