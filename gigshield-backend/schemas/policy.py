import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class PolicyCreate(BaseModel):
    worker_id: str
    zone_pincode: str


class PolicyResponse(BaseModel):
    id: str
    worker_id: str
    week_start_date: datetime.date
    week_end_date: datetime.date
    premium_paid: float
    max_coverage_amount: float
    coverage_remaining: float
    status: str
    zone_pincode: str
    created_at: datetime.datetime

    premium_breakdown: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class PolicySummary(BaseModel):
    id: str
    status: str
    week_start_date: datetime.date
    week_end_date: datetime.date
    premium_paid: float
    max_coverage_amount: float
    coverage_remaining: float

    model_config = ConfigDict(from_attributes=True)

