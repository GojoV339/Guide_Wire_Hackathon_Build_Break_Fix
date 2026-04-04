import random
from datetime import datetime

from sqlalchemy.orm import Session

from models.claim import Claim
from models.payout import Payout
from models.policy import Policy


def process_payout(claim_id: str, db: Session) -> dict:
    """Simulate UPI payout via Razorpay mock."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return {"error": "Claim not found"}

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand_suffix = random.randint(1000, 9999)
    transaction_id = f"GS-{timestamp}-{rand_suffix}"

    payout = Payout(
        claim_id=claim_id,
        amount=claim.payout_amount,
        upi_transaction_id=transaction_id,
        status="success",
        paid_at=datetime.utcnow(),
    )
    db.add(payout)

    policy = db.query(Policy).filter(Policy.id == claim.policy_id).first()
    if policy:
        policy.coverage_remaining = max(0, policy.coverage_remaining - claim.payout_amount)

    claim.status = "approved"
    db.commit()
    db.refresh(payout)

    print(f"[PAYOUT] Rs{claim.payout_amount} sent. TXN: {transaction_id}")
    return {
        "transaction_id": transaction_id,
        "amount": claim.payout_amount,
        "status": "success",
    }
