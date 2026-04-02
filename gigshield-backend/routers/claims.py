import datetime
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from models.worker import Worker
from schemas.disruption import DisruptionEventResponse
from services.auth_service import get_current_worker
from services.fraud_service import calculate_fraud_score
from services.fraud_service import is_claim_auto_approvable
from services.premium_service import calculate_payout_amount
from services.payout_service import generate_mock_transaction_id
from models.payout import Payout

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT") or "development"

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("/my-claims", status_code=status.HTTP_200_OK)
def my_claims(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> list[dict[str, Any]]:
    """Return all claims for the worker's policies, including disruption event details."""
    try:
        claims = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(Policy.worker_id == current_worker.id)
            .order_by(Claim.created_at.desc())
            .all()
        )
        results: list[dict[str, Any]] = []
        for c in claims:
            results.append(
                {
                    "claim": c,
                    "event": c.event,
                    "policy": c.policy,
                    "payout": c.payout,
                }
            )
        return results
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch claims: {e}")


@router.get("/active-disruptions", response_model=list[DisruptionEventResponse], status_code=status.HTTP_200_OK)
def active_disruptions(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> list[DisruptionEvent]:
    """Return all active disruption events for the current worker's active policy pincode."""
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

        events = (
            db.query(DisruptionEvent)
            .filter(and_(DisruptionEvent.zone_pincode == policy.zone_pincode, DisruptionEvent.is_active == True))
            .order_by(DisruptionEvent.started_at.desc())
            .all()
        )
        return events
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch active disruptions: {e}")


@router.post("/manual-trigger", status_code=status.HTTP_201_CREATED)
def manual_trigger(
    event_type: str = Body(..., embed=True),
    pincode: str = Body(..., embed=True),
    x_env_check: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Development-only: create a mock disruption event and process claims for all active policies in that pincode."""
    if ENVIRONMENT != "development":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Manual trigger disabled")

    try:
        now = datetime.datetime.utcnow()
        event = DisruptionEvent(
            event_type=event_type,
            zone_pincode=pincode,
            started_at=now,
            ended_at=None,
            severity_value=1.0,
            api_source="manual_trigger",
            verified=True,
            is_active=True,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        today = datetime.date.today()
        policies = (
            db.query(Policy)
            .filter(
                and_(
                    Policy.status == "active",
                    Policy.zone_pincode == pincode,
                    Policy.week_start_date <= today,
                    Policy.week_end_date >= today,
                )
            )
            .all()
        )

        created = 0
        for policy in policies:
            existing = db.query(Claim).filter(and_(Claim.policy_id == policy.id, Claim.event_id == event.id)).first()
            if existing:
                continue

            worker = policy.worker
            duration_hours = 1.0
            fraud_score = calculate_fraud_score(worker_id=worker.id, event_id=event.id, db=db)
            payout_amount = calculate_payout_amount(
                event_type=event.event_type,
                duration_hours=duration_hours,
                daily_earnings=worker.daily_earnings_declared,
                coverage_remaining=policy.coverage_remaining,
            )

            claim = Claim(
                policy_id=policy.id,
                event_id=event.id,
                payout_amount=float(payout_amount),
                fraud_score=float(fraud_score),
                status="pending",
                created_at=now,
                updated_at=now,
            )
            db.add(claim)
            db.commit()
            db.refresh(claim)
            created += 1

            if is_claim_auto_approvable(fraud_score):
                claim.status = "approved"
                payout = Payout(
                    claim_id=claim.id,
                    amount=float(payout_amount),
                    upi_transaction_id=generate_mock_transaction_id(),
                    status="success",
                    paid_at=now,
                    created_at=now,
                )
                policy.coverage_remaining = max(0.0, float(policy.coverage_remaining) - float(payout_amount))
                db.add(payout)
                db.add(policy)
                db.add(claim)
                db.commit()
            else:
                claim.status = "under_review"
                db.add(claim)
                db.commit()

        return {"event_id": event.id, "claims_created": created}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Manual trigger failed: {e}")


@router.get("/{claim_id}", status_code=status.HTTP_200_OK)
def get_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
) -> dict[str, Any]:
    """Return a single claim with full details and verify it belongs to the current worker."""
    try:
        claim = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(and_(Claim.id == claim_id, Policy.worker_id == current_worker.id))
            .first()
        )
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
        return {"claim": claim, "event": claim.event, "policy": claim.policy, "payout": claim.payout}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch claim: {e}")

