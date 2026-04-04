import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    amount = Column(Float, nullable=False)
    upi_transaction_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    claim = relationship("Claim", backref="payouts")
