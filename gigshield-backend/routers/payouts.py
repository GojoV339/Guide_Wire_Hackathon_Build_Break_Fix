import datetime
import random
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.payout import Payout
from models.policy import Policy
from models.worker import Worker
from schemas.payout import PayoutResponse
from services.auth_service import get_current_worker
from utils.helpers import get_month_bounds_for_date

router = APIRouter(prefix="/payouts", tags=["payouts"])


@router.get("/my-payouts", response_model=list[PayoutResponse], status_code=status.HTTP_200_OK)
def my_payouts(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> list[Payout]:
    """Return all payouts for the authenticated worker ordered by newest first."""
    try:
        payouts = (
            db.query(Payout)
            .join(Claim, Payout.claim_id == Claim.id)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(Policy.worker_id == current_worker.id)
            .order_by(Payout.created_at.desc())
            .all()
        )
        return payouts
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch payouts: {e}")


@router.get("/total-this-month", status_code=status.HTTP_200_OK)
def total_this_month(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> dict[str, Any]:
    """Return total payout amount received by this worker in the current month."""
    try:
        today = datetime.date.today()
        month_start, month_end = get_month_bounds_for_date(today)

        payouts = (
            db.query(Payout)
            .join(Claim, Payout.claim_id == Claim.id)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(
                and_(
                    Policy.worker_id == current_worker.id,
                    Payout.status == "success",
                    Payout.created_at >= month_start,
                    Payout.created_at <= month_end,
                )
            )
            .all()
        )
        total = float(sum(p.amount for p in payouts))
        return {"total_this_month": total}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to compute total payouts: {e}")


@router.post("/process/{claim_id}", status_code=status.HTTP_200_OK)
def process_payout(
    claim_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Internal: process payout for a claim (simulates Razorpay sandbox payment)."""
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rnd = random.randint(1000, 9999)
        tx_id = f"GS-{ts}-{rnd}"

        payout = db.query(Payout).filter(Payout.claim_id == claim.id).first()
        if payout:
            payout.status = "success"
            payout.upi_transaction_id = payout.upi_transaction_id or tx_id
            payout.paid_at = payout.paid_at or datetime.datetime.utcnow()
        else:
            payout = Payout(
                claim_id=claim.id,
                amount=float(claim.payout_amount),
                upi_transaction_id=tx_id,
                status="success",
                paid_at=datetime.datetime.utcnow(),
            )
            db.add(payout)

        db.commit()
        db.refresh(payout)
        return {"payout": payout}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process payout: {e}")
