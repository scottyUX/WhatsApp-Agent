from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class PatientImageSubmissionModel(BaseModel):
    id: UUID
    patient_profile_id: UUID
    image_urls: List[str]
    analysis: Optional[Dict[str, Any]] = None
    analysis_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
