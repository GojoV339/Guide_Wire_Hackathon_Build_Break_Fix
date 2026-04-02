import datetime
from uuid import uuid4

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import relationship

from database import Base


class DisruptionEvent(Base):
    __tablename__ = "disruption_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    event_type = Column(String, nullable=False)  # rain/aqi/heat/curfew/app_outage
    zone_pincode = Column(String, nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    severity_value = Column(Float, nullable=False)
    api_source = Column(String, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    claims = relationship("Claim", back_populates="event", cascade="all, delete-orphan")

