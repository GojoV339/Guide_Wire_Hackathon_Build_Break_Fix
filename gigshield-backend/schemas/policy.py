from datetime import date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PolicyCreateRequest(BaseModel):
    zone_pincode: str
    zone_name: Optional[str] = None


class PremiumQuoteResponse(BaseModel):
    base_premium: float
    earnings_linked: float
    zone_risk_loading: float
    claims_surcharge: float
    total_premium: float
    max_coverage: float
    risk_score: float
    risk_reasoning: Optional[str]


class PolicyResponse(BaseModel):
    id: str
    worker_id: str
    week_start_date: date
    week_end_date: date
    premium_paid: float
    max_coverage_amount: float
    coverage_remaining: float
    status: str
    zone_pincode: str
    zone_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
