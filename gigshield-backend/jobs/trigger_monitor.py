import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import SessionLocal
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.payout import Payout
from models.policy import Policy
from services.fraud_service import calculate_fraud_score
from services.fraud_service import is_claim_auto_approvable
from services.payout_service import generate_mock_transaction_id
from services.premium_service import calculate_payout_amount
from services.trigger_service import run_all_triggers_for_pincode


def process_triggers(db: Session) -> None:
    print("[GigShield TriggerMonitor] Running trigger scan...")

    today = datetime.date.today()
    active_policies = (
        db.query(Policy)
        .filter(
            and_(
                Policy.status == "active",
                Policy.week_start_date <= today,
                Policy.week_end_date >= today,
            )
        )
        .all()
    )
    pincodes = sorted({p.zone_pincode for p in active_policies})
    print(f"[GigShield TriggerMonitor] Active pincodes: {pincodes}")

    for pincode in pincodes:
        triggers = run_all_triggers_for_pincode(pincode)
        if triggers:
            print(f"[GigShield TriggerMonitor] Triggers fired for {pincode}: {triggers}")
        for trigger in triggers:
            now = datetime.datetime.utcnow()
            cutoff = now - datetime.timedelta(hours=2)
            existing = (
                db.query(DisruptionEvent)
                .filter(
                    and_(
                        DisruptionEvent.zone_pincode == pincode,
                        DisruptionEvent.event_type == trigger["event_type"],
                        DisruptionEvent.started_at >= cutoff,
                    )
                )
                .order_by(DisruptionEvent.started_at.desc())
                .first()
            )

            event = existing
            if not event:
                event = DisruptionEvent(
                    event_type=trigger["event_type"],
                    zone_pincode=pincode,
                    started_at=now,
                    ended_at=None,
                    severity_value=float(trigger["severity_value"]),
                    api_source=str(trigger["api_source"]),
                    verified=True,
                    is_active=True,
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                print(
                    f"[GigShield TriggerMonitor] Created disruption event {event.id} "
                    f"type={event.event_type} pincode={event.zone_pincode}"
                )

            zone_policies = (
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

            for policy in zone_policies:
                existing_claim = (
                    db.query(Claim)
                    .filter(and_(Claim.policy_id == policy.id, Claim.event_id == event.id))
                    .first()
                )
                if existing_claim:
                    continue

                duration_hours = max(
                    0.0,
                    (now - event.started_at).total_seconds() / 3600.0,
                )

                worker = policy.worker
                if not worker:
                    continue

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
                    db.add(payout)

                    policy.coverage_remaining = max(0.0, float(policy.coverage_remaining) - float(payout_amount))
                    db.add(policy)
                    db.add(claim)
                    db.commit()
                    print(
                        f"[GigShield TriggerMonitor] Auto-approved claim {claim.id} payout={payout_amount} "
                        f"fraud_score={fraud_score:.2f}"
                    )
                else:
                    claim.status = "under_review"
                    db.add(claim)
                    db.commit()
                    print(
                        f"[GigShield TriggerMonitor] Claim {claim.id} under review fraud_score={fraud_score:.2f}"
                    )


def _job_wrapper() -> None:
    db = SessionLocal()
    try:
        process_triggers(db)
    except Exception as e:
        print(f"[GigShield TriggerMonitor] Job error: {e}")
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(_job_wrapper, "interval", minutes=15, id="gigshield_trigger_monitor")
    scheduler.start()
    print("[GigShield TriggerMonitor] Scheduler started (every 15 minutes).")
    return scheduler

