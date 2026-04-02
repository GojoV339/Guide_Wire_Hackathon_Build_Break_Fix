import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class PayoutResponse(BaseModel):
    id: str
    claim_id: str
    amount: float
    upi_transaction_id: str | None
    status: str
    paid_at: datetime.datetime | None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

