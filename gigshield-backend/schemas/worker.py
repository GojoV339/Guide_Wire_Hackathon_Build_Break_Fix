import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class WorkerCreate(BaseModel):
    phone_number: str
    home_zone_pincode: str
    daily_earnings_declared: float


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    aadhaar_verified: Optional[bool] = None
    platform_partner_id: Optional[str] = None
    upi_id: Optional[str] = None


class WorkerResponse(BaseModel):
    id: str
    phone_number: str
    name: Optional[str]
    aadhaar_verified: bool
    platform_partner_id: Optional[str]
    home_zone_pincode: str
    daily_earnings_declared: float
    upi_id: Optional[str]
    risk_score: float
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    otp: Optional[str]
    otp_expires_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)


class OTPRequest(BaseModel):
    phone_number: str


class OTPVerify(BaseModel):
    phone_number: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    worker_id: str

