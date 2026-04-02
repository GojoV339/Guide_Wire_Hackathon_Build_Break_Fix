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
from models.policy import Policy
from models.worker import Worker
from schemas.policy import PolicyResponse
from services.auth_service import get_current_worker
from services.premium_service import calculate_risk_score
from services.premium_service import calculate_weekly_premium
from utils.helpers import get_monday_sunday_for_date
from utils.helpers import get_month_bounds_for_date

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_policy(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> dict[str, Any]:
    """Create a new weekly policy for the authenticated worker if none exists for current week."""
    try:
        today = datetime.date.today()
        week_start, week_end = get_monday_sunday_for_date(today)

        existing = (
            db.query(Policy)
            .filter(
                and_(
                    Policy.worker_id == current_worker.id,
                    Policy.status == "active",
                    Policy.week_start_date == week_start,
                    Policy.week_end_date == week_end,
                )
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Worker already has active policy")

        risk_score = float(calculate_risk_score(current_worker.home_zone_pincode, db))

        month_start, month_end = get_month_bounds_for_date(today)
        prior_claims = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(
                and_(
                    Policy.worker_id == current_worker.id,
                    Claim.created_at >= month_start,
                    Claim.created_at <= month_end,
                )
            )
            .count()
        )

        breakdown = calculate_weekly_premium(
            daily_earnings=float(current_worker.daily_earnings_declared),
            risk_score=risk_score,
            prior_claims_this_month=int(prior_claims),
        )

        policy = Policy(
            worker_id=current_worker.id,
            week_start_date=week_start,
            week_end_date=week_end,
            premium_paid=float(breakdown["total_premium"]),
            max_coverage_amount=float(breakdown["max_coverage"]),
            coverage_remaining=float(breakdown["max_coverage"]),
            status="active",
            zone_pincode=current_worker.home_zone_pincode,
        )

        current_worker.risk_score = risk_score
        db.add(current_worker)
        db.add(policy)
        db.commit()
        db.refresh(policy)

        return {"policy": policy, "premium_breakdown": breakdown}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create policy: {e}")


@router.get("/current", response_model=PolicyResponse, status_code=status.HTTP_200_OK)
def current_policy(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> Policy:
    """Return the worker's current active policy for this week or 404 if none."""
    try:
        today = datetime.date.today()
        policy = (
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
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active policy found")
        return policy
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to get current policy: {e}")


@router.get("/history", response_model=list[PolicyResponse], status_code=status.HTTP_200_OK)
def policy_history(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> list[Policy]:
    """Return all policies for the authenticated worker ordered by newest first."""
    try:
        policies = (
            db.query(Policy)
            .filter(Policy.worker_id == current_worker.id)
            .order_by(Policy.created_at.desc())
            .all()
        )
        return policies
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to get policy history: {e}")


@router.get("/premium-quote", status_code=status.HTTP_200_OK)
def premium_quote(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> dict[str, Any]:
    """Return a premium quote breakdown without creating a policy."""
    try:
        today = datetime.date.today()
        risk_score = float(calculate_risk_score(current_worker.home_zone_pincode, db))

        month_start, month_end = get_month_bounds_for_date(today)
        prior_claims = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(
                and_(
                    Policy.worker_id == current_worker.id,
                    Claim.created_at >= month_start,
                    Claim.created_at <= month_end,
                )
            )
            .count()
        )

        breakdown = calculate_weekly_premium(
            daily_earnings=float(current_worker.daily_earnings_declared),
            risk_score=risk_score,
            prior_claims_this_month=int(prior_claims),
        )
        return {"premium_breakdown": breakdown}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to get premium quote: {e}")

