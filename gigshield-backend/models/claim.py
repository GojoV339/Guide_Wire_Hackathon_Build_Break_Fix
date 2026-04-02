import datetime
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False, index=True)
    event_id = Column(String, ForeignKey("disruption_events.id"), nullable=False, index=True)

    payout_amount = Column(Float, nullable=False)
    fraud_score = Column(Float, default=0.0, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending/approved/rejected/under_review

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    policy = relationship("Policy", back_populates="claims")
    event = relationship("DisruptionEvent", back_populates="claims")
    payout = relationship("Payout", back_populates="claim", uselist=False, cascade="all, delete-orphan")

