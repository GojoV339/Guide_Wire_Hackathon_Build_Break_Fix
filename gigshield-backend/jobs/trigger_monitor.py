import json
from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import SessionLocal
from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from services.fraud_service import analyze_claim
from services.llm_service import calculate_payout_llm
from services.payout_service import process_payout
from services.trigger_service import run_all_triggers


def process_triggers():
    """Main job that runs every 15 minutes to check for disruptions."""
    print(f"\n[MONITOR] Running trigger check at {datetime.utcnow()}")
    db = SessionLocal()
    try:
        active_policies = db.query(Policy).filter(Policy.status == "active").all()

        pincodes = list(set(p.zone_pincode for p in active_policies))
        print(f"[MONITOR] Checking {len(pincodes)} zones: {pincodes}")

        for pincode in pincodes:
            triggers = run_all_triggers(pincode)
            for trigger_data in triggers:
                two_hours_ago = datetime.utcnow() - timedelta(hours=2)
                existing = (
                    db.query(DisruptionEvent)
                    .filter(
                        and_(
                            DisruptionEvent.zone_pincode == pincode,
                            DisruptionEvent.event_type == trigger_data["event_type"],
                            DisruptionEvent.created_at >= two_hours_ago,
                            DisruptionEvent.is_active == True,
                        )
                    )
                    .first()
                )

                if not existing:
                    event = DisruptionEvent(
                        event_type=trigger_data["event_type"],
                        zone_pincode=pincode,
                        severity_value=trigger_data["severity_value"],
                        api_source=trigger_data["api_source"],
                        verified=True,
                        is_active=True,
                    )
                    db.add(event)
                    db.commit()
                    db.refresh(event)
                    print(f"[MONITOR] New event: {event.event_type} in {pincode}")

                    zone_policies = [p for p in active_policies if p.zone_pincode == pincode]

                    for policy in zone_policies:
                        existing_claim = (
                            db.query(Claim)
                            .filter(and_(Claim.policy_id == policy.id, Claim.event_id == event.id))
                            .first()
                        )

                        if existing_claim:
                            continue

                        duration = 2.0
                        w = policy.worker
                        daily_earnings = w.daily_earnings_declared if w else 700.0
                        payout_result = calculate_payout_llm(
                            event_type=event.event_type,
                            event_severity=event.severity_value,
                            duration_hours=duration,
                            daily_earnings=daily_earnings,
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
                            print(f"[MONITOR] Auto-approved Rs{claim.payout_amount} for worker {policy.worker_id}")
                        elif fraud_result["decision"] == "reject":
                            claim.status = "rejected"
                            db.commit()
                            print(f"[MONITOR] Rejected claim for worker {policy.worker_id}")
                        else:
                            claim.status = "under_review"
                            db.commit()
                            print(f"[MONITOR] Manual review needed for worker {policy.worker_id}")

    except Exception as e:
        print(f"[MONITOR ERROR] {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_triggers, "interval", minutes=15, id="trigger_monitor")
    scheduler.start()
    print("[SCHEDULER] Trigger monitor started. Runs every 15 minutes.")
    return scheduler
