from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.payout import Payout
from models.policy import Policy
from models.worker import Worker
from services.auth_service import get_current_worker

router = APIRouter(prefix="/payouts", tags=["Payouts"])


@router.get("/my-payouts")
def get_my_payouts(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get all payouts for the current worker."""
    payouts = (
        db.query(Payout)
        .join(Claim, Payout.claim_id == Claim.id)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(
            Policy.worker_id == current_worker.id,
            Payout.status == "success",
        )
        .order_by(Payout.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "amount": p.amount,
            "transaction_id": p.upi_transaction_id,
            "status": p.status,
            "paid_at": str(p.paid_at),
            "claim_id": p.claim_id,
        }
        for p in payouts
    ]


@router.get("/total-this-month")
def get_monthly_total(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get total payouts received this month."""
    start_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    payouts = (
        db.query(Payout)
        .join(Claim, Payout.claim_id == Claim.id)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(
            Policy.worker_id == current_worker.id,
            Payout.status == "success",
            Payout.created_at >= start_month,
        )
        .all()
    )
    total = sum(p.amount for p in payouts)
    return {"total_this_month": total, "count": len(payouts)}
