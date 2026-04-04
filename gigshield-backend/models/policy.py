import uuid

from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String, ForeignKey("workers.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    premium_paid = Column(Float, nullable=False)
    max_coverage_amount = Column(Float, nullable=False)
    coverage_remaining = Column(Float, nullable=False)
    status = Column(String, default="active")
    zone_pincode = Column(String, nullable=False)
    zone_name = Column(String, nullable=True)
    premium_breakdown = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    worker = relationship("Worker", backref="policies")
