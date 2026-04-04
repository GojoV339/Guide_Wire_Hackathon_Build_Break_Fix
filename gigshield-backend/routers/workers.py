from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.payout import Payout
from models.policy import Policy
from models.worker import Worker
from schemas.worker import WorkerProfileUpdate
from services.auth_service import get_current_worker
from services.premium_service import calculate_risk_score

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.put("/profile")
def update_profile(
    update: WorkerProfileUpdate,
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Update worker profile and recalculate risk score."""
    if update.name is not None:
        current_worker.name = update.name
    if update.home_zone_pincode is not None:
        current_worker.home_zone_pincode = update.home_zone_pincode
    if update.home_zone_name is not None:
        current_worker.home_zone_name = update.home_zone_name
    if update.daily_earnings_declared is not None:
        current_worker.daily_earnings_declared = update.daily_earnings_declared
    if update.upi_id is not None:
        current_worker.upi_id = update.upi_id
    if update.platform_partner_id is not None:
        current_worker.platform_partner_id = update.platform_partner_id

    if current_worker.home_zone_pincode:
        risk_result = calculate_risk_score(
            current_worker.home_zone_pincode,
            current_worker.home_zone_name or current_worker.home_zone_pincode,
            db,
        )
        current_worker.risk_score = risk_result["risk_score"]
        current_worker.risk_reasoning = risk_result["reasoning"]

    db.commit()
    db.refresh(current_worker)
    return {
        "message": "Profile updated",
        "risk_score": current_worker.risk_score,
        "risk_reasoning": current_worker.risk_reasoning,
    }


@router.get("/profile")
def get_profile(current_worker: Worker = Depends(get_current_worker)):
    """Get full worker profile."""
    return {
        "id": current_worker.id,
        "phone_number": current_worker.phone_number,
        "name": current_worker.name,
        "home_zone_pincode": current_worker.home_zone_pincode,
        "home_zone_name": current_worker.home_zone_name,
        "daily_earnings_declared": current_worker.daily_earnings_declared,
        "upi_id": current_worker.upi_id,
        "platform_partner_id": current_worker.platform_partner_id,
        "risk_score": current_worker.risk_score,
        "risk_reasoning": current_worker.risk_reasoning,
        "aadhaar_verified": current_worker.aadhaar_verified,
    }


@router.get("/dashboard")
def get_dashboard(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get worker dashboard summary."""
    active_policy = (
        db.query(Policy)
        .filter(
            Policy.worker_id == current_worker.id,
            Policy.status == "active",
        )
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

    start_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_payouts = (
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

    total_received = sum(p.amount for p in monthly_payouts)

    active_disruptions = []
    if active_policy and active_policy.zone_pincode:
        active_disruptions = (
            db.query(DisruptionEvent)
            .filter(
                DisruptionEvent.zone_pincode == active_policy.zone_pincode,
                DisruptionEvent.is_active == True,
            )
            .all()
        )

    return {
        "worker_name": current_worker.name,
        "risk_score": current_worker.risk_score,
        "active_policy": {
            "id": active_policy.id,
            "coverage_remaining": active_policy.coverage_remaining,
            "max_coverage": active_policy.max_coverage_amount,
            "week_end": str(active_policy.week_end_date),
            "status": active_policy.status,
        }
        if active_policy
        else None,
        "recent_claims": [
            {
                "id": c.id,
                "status": c.status,
                "amount": c.payout_amount,
                "created_at": str(c.created_at),
            }
            for c in recent_claims
        ],
        "active_disruptions": [
            {
                "id": str(d.id),
                "event_type": d.event_type,
                "severity_value": float(d.severity_value) if d.severity_value else 0.0,
                "api_source": d.api_source,
                "created_at": str(d.created_at),
            }
            for d in active_disruptions
        ],
        "total_received_this_month": total_received,
    }
