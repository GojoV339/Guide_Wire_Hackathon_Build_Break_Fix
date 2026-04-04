import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.policy import Policy
from models.worker import Worker
from schemas.policy import PolicyCreateRequest
from services.auth_service import get_current_worker
from services.premium_service import calculate_premium
from services.premium_service import calculate_risk_score
from services.premium_service import get_prior_claims_count
from services.premium_service import get_week_dates

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("/premium-quote")
def get_premium_quote(
    zone_pincode: str,
    zone_name: str = "",
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get premium quote without creating a policy."""
    risk_result = calculate_risk_score(zone_pincode, zone_name or zone_pincode, db)
    prior_claims = get_prior_claims_count(current_worker.id, db)
    premium = calculate_premium(
        current_worker.daily_earnings_declared,
        risk_result["risk_score"],
        prior_claims,
    )
    return {
        **premium,
        "risk_score": risk_result["risk_score"],
        "risk_category": risk_result.get("risk_category", "medium"),
        "risk_reasoning": risk_result["reasoning"],
    }


@router.post("/create")
def create_policy(
    request: PolicyCreateRequest,
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Create a new weekly policy for the worker."""
    monday, sunday = get_week_dates()
    existing = (
        db.query(Policy)
        .filter(
            Policy.worker_id == current_worker.id,
            Policy.status == "active",
            Policy.week_start_date == monday,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="You already have an active policy this week")

    risk_result = calculate_risk_score(
        request.zone_pincode,
        request.zone_name or request.zone_pincode,
        db,
    )

    current_worker.risk_score = risk_result["risk_score"]
    current_worker.risk_reasoning = risk_result["reasoning"]

    prior_claims = get_prior_claims_count(current_worker.id, db)
    premium = calculate_premium(
        current_worker.daily_earnings_declared,
        risk_result["risk_score"],
        prior_claims,
    )

    policy = Policy(
        worker_id=current_worker.id,
        week_start_date=monday,
        week_end_date=sunday,
        premium_paid=premium["total_premium"],
        max_coverage_amount=premium["max_coverage"],
        coverage_remaining=premium["max_coverage"],
        status="active",
        zone_pincode=request.zone_pincode,
        zone_name=request.zone_name,
        premium_breakdown=json.dumps(premium),
    )
    db.add(policy)
    db.add(current_worker)
    db.commit()
    db.refresh(policy)

    return {
        "message": "Policy created successfully",
        "policy_id": policy.id,
        "premium_paid": policy.premium_paid,
        "max_coverage": policy.max_coverage_amount,
        "week_start": str(policy.week_start_date),
        "week_end": str(policy.week_end_date),
        "risk_score": risk_result["risk_score"],
        "risk_reasoning": risk_result["reasoning"],
        "premium_breakdown": premium,
    }


@router.get("/current")
def get_current_policy(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get worker's current active policy."""
    policy = (
        db.query(Policy)
        .filter(
            Policy.worker_id == current_worker.id,
            Policy.status == "active",
        )
        .first()
    )
    if not policy:
        raise HTTPException(status_code=404, detail="No active policy found")
    return {
        "id": policy.id,
        "week_start_date": str(policy.week_start_date),
        "week_end_date": str(policy.week_end_date),
        "premium_paid": policy.premium_paid,
        "max_coverage_amount": policy.max_coverage_amount,
        "coverage_remaining": policy.coverage_remaining,
        "status": policy.status,
        "zone_pincode": policy.zone_pincode,
        "zone_name": policy.zone_name,
    }


@router.get("/history")
def get_policy_history(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get all policies for the worker."""
    policies = (
        db.query(Policy)
        .filter(Policy.worker_id == current_worker.id)
        .order_by(Policy.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "week_start": str(p.week_start_date),
            "week_end": str(p.week_end_date),
            "premium_paid": p.premium_paid,
            "max_coverage": p.max_coverage_amount,
            "coverage_remaining": p.coverage_remaining,
            "status": p.status,
            "zone_pincode": p.zone_pincode,
        }
        for p in policies
    ]
