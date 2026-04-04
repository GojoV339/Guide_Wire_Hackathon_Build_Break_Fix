import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)
    event_id = Column(String, ForeignKey("disruption_events.id"), nullable=False)
    payout_amount = Column(Float, nullable=False)
    fraud_score = Column(Float, default=0.0)
    fraud_reasoning = Column(String, nullable=True)
    fraud_indicators = Column(String, nullable=True)
    status = Column(String, default="pending")
    calculation_explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    policy = relationship("Policy", backref="claims")
    event = relationship("DisruptionEvent", backref="claims")
