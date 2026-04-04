import json
from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from models.payout import Payout
from services.llm_service import get_forecast_llm
from services.premium_service import get_current_season
import services.trigger_service as trigger_service
from jobs.trigger_monitor import process_triggers

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db)):
    """Admin dashboard with all key metrics and LLM forecast."""
    start_week = datetime.utcnow() - timedelta(days=7)
    start_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    active_policies = db.query(Policy).filter(Policy.status == "active").count()

    premiums_this_week = db.query(Policy).filter(Policy.created_at >= start_week).all()
    total_premiums = sum(p.premium_paid for p in premiums_this_week)

    payouts_this_week = (
        db.query(Payout)
        .filter(
            Payout.status == "success",
            Payout.created_at >= start_week,
        )
        .all()
    )
    total_payouts = sum(p.amount for p in payouts_this_week)

    loss_ratio = round((total_payouts / total_premiums * 100), 1) if total_premiums > 0 else 0

    fraud_alerts = db.query(Claim).filter(Claim.status == "under_review").count()

    all_active = db.query(Policy).filter(Policy.status == "active").all()
    pincodes = list(set(p.zone_pincode for p in all_active))

    zone_breakdown = []
    for pincode in pincodes:
        workers = len([p for p in all_active if p.zone_pincode == pincode])
        zone_claims = (
            db.query(Claim)
            .join(Policy, Claim.policy_id == Policy.id)
            .filter(
                Policy.zone_pincode == pincode,
                Claim.created_at >= start_week,
            )
            .count()
        )
        risk_scores = [
            p.worker.risk_score
            for p in all_active
            if p.zone_pincode == pincode and p.worker
        ]
        avg_risk = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 5.0
        zone_breakdown.append(
            {
                "pincode": pincode,
                "active_workers": workers,
                "claims_this_week": zone_claims,
                "avg_risk_score": avg_risk,
            }
        )

    recent_claim_types = []
    recent_claims = db.query(Claim).filter(Claim.created_at >= start_week).all()
    for c in recent_claims:
        ev = c.event
        if ev and ev.event_type not in recent_claim_types:
            recent_claim_types.append(ev.event_type)

    forecast = get_forecast_llm(
        city="Bengaluru",
        active_pincodes=pincodes,
        season=get_current_season(),
        recent_claim_types=recent_claim_types,
    )

    return {
        "summary": {
            "active_policies": active_policies,
            "premiums_collected_this_week": round(total_premiums, 2),
            "claims_paid_this_week": round(total_payouts, 2),
            "loss_ratio_percent": loss_ratio,
            "fraud_alerts_pending": fraud_alerts,
        },
        "zone_breakdown": zone_breakdown,
        "ai_forecast": forecast,
    }


@router.get("/fraud-queue")
def get_fraud_queue(db: Session = Depends(get_db)):
    """Get all claims pending manual review."""
    claims = db.query(Claim).filter(Claim.status == "under_review").order_by(Claim.created_at.desc()).all()

    out = []
    for c in claims:
        indicators = []
        if c.fraud_indicators:
            try:
                indicators = json.loads(c.fraud_indicators)
            except json.JSONDecodeError:
                indicators = []
        ev = c.event
        out.append(
            {
                "claim_id": c.id,
                "policy_id": c.policy_id,
                "payout_amount": c.payout_amount,
                "fraud_score": c.fraud_score,
                "fraud_reasoning": c.fraud_reasoning,
                "fraud_indicators": indicators,
                "event_type": ev.event_type if ev else None,
                "created_at": str(c.created_at),
            }
        )
    return out


@router.post("/demo/force-trigger")
def force_demo_trigger(db: Session = Depends(get_db)):
    """DEMO ONLY: Instantly simulates a major system outage and runs the auto-claimer."""
    # Activate the mock outage
    trigger_service.MOCK_OUTAGE_ACTIVE = True
    
    # Run the background scheduler job immediately
    try:
        process_triggers()
    finally:
        # Turn it off so it doesn't loop forever
        trigger_service.MOCK_OUTAGE_ACTIVE = False
        
    return {"message": "Simulated Platform Outage disruption successfully triggered. Claims have been automatically evaluated via LLM and processed."}


@router.post("/demo/reset-disruptions")
def reset_demo_disruptions(db: Session = Depends(get_db)):
    """DEMO ONLY: Deactivates all active disruption events to clear the dashboard."""
    active_events = db.query(DisruptionEvent).filter(DisruptionEvent.is_active == True).all()
    for event in active_events:
        event.is_active = False
    db.commit()
    return {"message": f"Successfully deactivated {len(active_events)} active disruption events."}
