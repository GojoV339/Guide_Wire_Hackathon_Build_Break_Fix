import json
import os

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from models.worker import Worker
from schemas.claim import ManualTriggerRequest
from services.auth_service import get_current_worker
from services.fraud_service import analyze_claim
from services.llm_service import calculate_payout_llm
from services.payout_service import process_payout

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("/my-claims")
def get_my_claims(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get all claims for the current worker."""
    claims = (
        db.query(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(Policy.worker_id == current_worker.id)
        .order_by(Claim.created_at.desc())
        .all()
    )

    result = []
    for c in claims:
        event = db.query(DisruptionEvent).filter(DisruptionEvent.id == c.event_id).first()
        result.append(
            {
                "id": c.id,
                "status": c.status,
                "payout_amount": c.payout_amount,
                "fraud_score": c.fraud_score,
                "fraud_reasoning": c.fraud_reasoning,
                "calculation": c.calculation_explanation,
                "created_at": str(c.created_at),
                "event_type": event.event_type if event else None,
                "event_severity": event.severity_value if event else None,
            }
        )
    return result


@router.get("/active-disruptions")
def get_active_disruptions(
    current_worker: Worker = Depends(get_current_worker),
    db: Session = Depends(get_db),
):
    """Get active disruptions in worker's zone."""
    policy = (
        db.query(Policy)
        .filter(
            Policy.worker_id == current_worker.id,
            Policy.status == "active",
        )
        .first()
    )

    if not policy:
        return {"disruptions": [], "message": "No active policy"}

    disruptions = (
        db.query(DisruptionEvent)
        .filter(
            DisruptionEvent.zone_pincode == policy.zone_pincode,
            DisruptionEvent.is_active == True,
        )
        .all()
    )

    return {
        "zone_pincode": policy.zone_pincode,
        "zone_name": policy.zone_name,
        "disruptions": [
            {
                "id": d.id,
                "event_type": d.event_type,
                "severity_value": d.severity_value,
                "started_at": str(d.started_at),
                "api_source": d.api_source,
            }
            for d in disruptions
        ],
    }


@router.post("/manual-trigger")
def manual_trigger(
    request: ManualTriggerRequest,
    db: Session = Depends(get_db),
):
    """Manually trigger a disruption event for testing. Dev mode only."""
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=403, detail="Only available in development")

    event = DisruptionEvent(
        event_type=request.event_type,
        zone_pincode=request.zone_pincode,
        severity_value=request.severity_value,
        api_source="manual_test",
        verified=True,
        is_active=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    print(f"[MANUAL] Created {request.event_type} event in {request.zone_pincode}")

    affected_policies = (
        db.query(Policy)
        .filter(
            Policy.zone_pincode == request.zone_pincode,
            Policy.status == "active",
        )
        .all()
    )

    claims_created = 0
    for policy in affected_policies:
        payout_result = calculate_payout_llm(
            event_type=request.event_type,
            event_severity=request.severity_value,
            duration_hours=request.duration_hours,
            daily_earnings=policy.worker.daily_earnings_declared if policy.worker else 700.0,
            coverage_remaining=policy.coverage_remaining,
        )

        fraud_result = analyze_claim(
            worker_id=policy.worker_id,
            event_id=event.id,
            policy_id=policy.id,
            db=db,
        )

        claim = Claim(
            policy_id=policy.id,
            event_id=event.id,
            payout_amount=payout_result["final_payout"],
            fraud_score=fraud_result["trust_score"],
            fraud_reasoning=fraud_result["reasoning"],
            fraud_indicators=json.dumps(fraud_result.get("fraud_indicators", [])),
            status="pending",
            calculation_explanation=payout_result["calculation_explanation"],
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)

        if fraud_result["decision"] == "auto_approve":
            process_payout(claim.id, db)
            print(f"[MANUAL] Payout Rs{claim.payout_amount} to worker {policy.worker_id}")
        elif fraud_result["decision"] == "reject":
            claim.status = "rejected"
            db.commit()
        else:
            claim.status = "under_review"
            db.commit()

        claims_created += 1

    return {
        "event_id": event.id,
        "claims_created": claims_created,
        "message": f"Triggered {request.event_type} in {request.zone_pincode}",
    }
