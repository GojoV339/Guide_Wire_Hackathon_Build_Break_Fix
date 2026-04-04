from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PayoutResponse(BaseModel):
    id: str
    claim_id: str
    amount: float
    upi_transaction_id: Optional[str]
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
