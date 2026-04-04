import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.sql import func

from database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    aadhaar_verified = Column(Boolean, default=False)
    platform_partner_id = Column(String, nullable=True)
    home_zone_pincode = Column(String, nullable=True)
    home_zone_name = Column(String, nullable=True)
    daily_earnings_declared = Column(Float, default=700.0)
    upi_id = Column(String, nullable=True)
    risk_score = Column(Float, default=5.0)
    risk_reasoning = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    otp = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
