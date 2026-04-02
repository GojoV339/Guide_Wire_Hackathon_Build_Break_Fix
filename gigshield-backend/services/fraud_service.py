import datetime

from fastapi import HTTPException
from fastapi import status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy


def calculate_fraud_score(worker_id: str, event_id: str, db: Session) -> float:
    trust_score = 1.0

    event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()
    if not event:
        trust_score -= 0.15
    else:
        if not event.verified:
            trust_score -= 0.15

    since_7d = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    claims_last_7d = (
        db.query(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(and_(Policy.worker_id == worker_id, Claim.created_at >= since_7d))
        .count()
    )
    if claims_last_7d > 3:
        trust_score -= 0.20

    duplicate = (
        db.query(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(and_(Policy.worker_id == worker_id, Claim.event_id == event_id))
        .first()
    )
    if duplicate:
        trust_score -= 0.40

    policy = (
        db.query(Policy)
        .filter(and_(Policy.worker_id == worker_id, Policy.status == "active"))
        .order_by(Policy.created_at.desc())
        .first()
    )
    if policy and event:
        if policy.created_at and event.started_at and policy.created_at > event.started_at:
            trust_score -= 0.30

    return max(0.0, float(trust_score))


def is_claim_auto_approvable(fraud_score: float) -> bool:
    return fraud_score >= 0.85

