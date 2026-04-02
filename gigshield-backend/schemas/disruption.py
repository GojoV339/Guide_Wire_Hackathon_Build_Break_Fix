import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class DisruptionEventCreate(BaseModel):
    event_type: str
    zone_pincode: str
    severity_value: float
    api_source: str


class DisruptionEventResponse(BaseModel):
    id: str
    event_type: str
    zone_pincode: str
    started_at: datetime.datetime
    ended_at: datetime.datetime | None
    severity_value: float
    api_source: str
    verified: bool
    is_active: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

