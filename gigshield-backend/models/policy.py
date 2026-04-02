import datetime
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False, index=True)

    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)

    premium_paid = Column(Float, nullable=False)
    max_coverage_amount = Column(Float, nullable=False)
    coverage_remaining = Column(Float, nullable=False)

    status = Column(String, default="active", nullable=False)  # active/expired/cancelled
    zone_pincode = Column(String, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    worker = relationship("Worker", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", cascade="all, delete-orphan")

