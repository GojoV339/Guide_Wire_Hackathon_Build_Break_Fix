import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ClaimResponse(BaseModel):
    id: str
    policy_id: str
    event_id: str
    payout_amount: float
    fraud_score: float
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimSummary(BaseModel):
    id: str
    status: str
    payout_amount: float
    fraud_score: float
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

