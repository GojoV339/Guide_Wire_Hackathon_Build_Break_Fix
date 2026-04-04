from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OTPRequest(BaseModel):
    phone_number: str


class OTPVerify(BaseModel):
    phone_number: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: str


class WorkerProfileUpdate(BaseModel):
    name: Optional[str] = None
    home_zone_pincode: Optional[str] = None
    home_zone_name: Optional[str] = None
    daily_earnings_declared: Optional[float] = None
    upi_id: Optional[str] = None
    platform_partner_id: Optional[str] = None


class WorkerResponse(BaseModel):
    id: str
    phone_number: str
    name: Optional[str]
    home_zone_pincode: Optional[str]
    home_zone_name: Optional[str]
    daily_earnings_declared: float
    upi_id: Optional[str]
    risk_score: float
    risk_reasoning: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
