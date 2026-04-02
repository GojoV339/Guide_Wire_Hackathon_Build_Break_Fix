import datetime
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
from schemas.worker import WorkerResponse
from schemas.worker import WorkerUpdate
from services.auth_service import get_current_worker
from services.premium_service import calculate_risk_score
from utils.helpers import get_month_bounds_for_date

router = APIRouter(prefix="/workers", tags=["workers"])


@router.put("/profile", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def update_profile(
    payload: WorkerUpdate,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> Worker:
    """Update current worker profile fields and recalculate risk score."""
    try:
        if payload.name is not None:
            current_worker.name = payload.name
        if payload.aadhaar_verified is not None:
            current_worker.aadhaar_verified = payload.aadhaar_verified
        if payload.platform_partner_id is not None:
            current_worker.platform_partner_id = payload.platform_partner_id
        if payload.upi_id is not None:
            current_worker.upi_id = payload.upi_id

        current_worker.risk_score = float(calculate_risk_score(current_worker.home_zone_pincode, db))
        db.add(current_worker)
        db.commit()
        db.refresh(current_worker)
        return current_worker
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {e}")


@router.get("/profile", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def get_profile(current_worker: Worker = Depends(get_current_worker)) -> Worker:
    """Return current worker full profile."""
    return current_worker


@router.get("/dashboard", status_code=status.HTTP_200_OK)
def dashboard(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> dict[str, Any]:
    """Return worker dashboard summary including active policy, recent claims, and payouts this month."""
    try:
        today = datetime.date.today()

        active_policy = (
            db.query(Policy)
            .filter(
                and_(
                    Policy.worker_id == current_worker.id,
                    Policy.status == "active",
                    Policy.week_start_date <= today,
                    Policy.week_end_date >= today,
                )
            )
            .order_by(Policy.created_at.desc())
            .first()
        )

        recent_claims = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(Policy.worker_id == current_worker.id)
            .order_by(Claim.created_at.desc())
            .limit(5)
            .all()
        )

        month_start, month_end = get_month_bounds_for_date(today)
        total_payouts_this_month = (
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
        total_amount = float(sum(p.amount for p in total_payouts_this_month))

        return {
            "worker": {
                "id": current_worker.id,
                "phone_number": current_worker.phone_number,
                "name": current_worker.name,
                "home_zone_pincode": current_worker.home_zone_pincode,
                "daily_earnings_declared": current_worker.daily_earnings_declared,
                "risk_score": current_worker.risk_score,
            },
            "active_policy": active_policy,
            "recent_claims": recent_claims,
            "total_payouts_received_this_month": total_amount,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {e}")

