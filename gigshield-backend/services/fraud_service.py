from datetime import datetime
from datetime import timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from models.worker import Worker
from services.llm_service import analyze_fraud_llm


def analyze_claim(
    worker_id: str,
    event_id: str,
    policy_id: str,
    db: Session,
) -> dict:
    """Analyze a claim for fraud using LLM."""
    event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()

    policy = db.query(Policy).filter(Policy.id == policy_id).first()

    worker = db.query(Worker).filter(Worker.id == worker_id).first()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_claims = (
        db.query(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(and_(Policy.worker_id == worker_id, Claim.created_at >= seven_days_ago))
        .count()
    )

    duplicate = (
        db.query(Claim)
        .filter(and_(Claim.policy_id == policy_id, Claim.event_id == event_id))
        .first()
    ) is not None

    policy_before_event = True
    if policy and event:
        policy_date = datetime.combine(policy.week_start_date, datetime.min.time())
        policy_before_event = policy_date <= event.started_at

    days_as_customer = 30
    if worker:
        days_as_customer = max(1, (datetime.utcnow() - worker.created_at).days)

    result = analyze_fraud_llm(
        event_type=event.event_type if event else "unknown",
        event_severity=event.severity_value if event else 0,
        zone_pincode=event.zone_pincode if event else "unknown",
        claims_last_7_days=recent_claims,
        policy_created_before_event=policy_before_event,
        event_verified_by_api=event.verified if event else False,
        is_duplicate=duplicate,
        days_as_customer=days_as_customer,
    )
    return result
