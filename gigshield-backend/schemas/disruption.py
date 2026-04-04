from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DisruptionEventResponse(BaseModel):
    id: str
    event_type: str
    zone_pincode: str
    started_at: datetime
    ended_at: Optional[datetime]
    severity_value: float
    api_source: str
    verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
