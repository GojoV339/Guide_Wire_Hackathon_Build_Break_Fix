from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClaimResponse(BaseModel):
    id: str
    policy_id: str
    event_id: str
    payout_amount: float
    fraud_score: float
    fraud_reasoning: Optional[str]
    status: str
    calculation_explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ManualTriggerRequest(BaseModel):
    event_type: str
    zone_pincode: str
    severity_value: float = 30.0
    duration_hours: float = 2.0
