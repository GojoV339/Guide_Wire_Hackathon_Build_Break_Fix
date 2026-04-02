import datetime
from uuid import uuid4

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import relationship

from database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    phone_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    aadhaar_verified = Column(Boolean, default=False, nullable=False)
    platform_partner_id = Column(String, nullable=True)
    home_zone_pincode = Column(String, nullable=False, default="000000")
    daily_earnings_declared = Column(Float, nullable=False, default=0.0)
    upi_id = Column(String, nullable=True)
    risk_score = Column(Float, default=5.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    otp = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    policies = relationship("Policy", back_populates="worker", cascade="all, delete-orphan")

