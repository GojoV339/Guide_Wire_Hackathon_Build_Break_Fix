from datetime import date
from datetime import datetime
from datetime import timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.claim import Claim
from models.disruption import DisruptionEvent
from models.policy import Policy
from services.llm_service import calculate_risk_score_llm


def get_current_season() -> str:
    """Return current season based on month."""
    month = datetime.now().month
    if month in [6, 7, 8, 9]:
        return "monsoon"
    elif month in [10, 11]:
        return "post_monsoon"
    elif month in [12, 1, 2]:
        return "winter"
    else:
        return "summer"


def get_week_dates():
    """Return Monday and Sunday of current week."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def calculate_risk_score(
    zone_pincode: str,
    zone_name: str,
    db: Session,
) -> dict:
    """Calculate risk score for a zone using LLM."""
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    count = (
        db.query(DisruptionEvent)
        .filter(
            and_(
                DisruptionEvent.zone_pincode == zone_pincode,
                DisruptionEvent.created_at >= ninety_days_ago,
            )
        )
        .count()
    )
    season = get_current_season()
    return calculate_risk_score_llm(zone_pincode, zone_name, count, season)


def calculate_premium(
    daily_earnings: float,
    risk_score: float,
    prior_claims_this_month: int,
) -> dict:
    """Calculate weekly premium breakdown."""
    base = 29.0
    weekly_earnings = daily_earnings * 7
    earnings_linked = round(weekly_earnings * 0.014, 2)
    zone_risk_loading = round(risk_score * 1.5, 2)
    claims_surcharge = round(prior_claims_this_month * 4.0, 2)
    total = round(base + earnings_linked + zone_risk_loading + claims_surcharge, 2)
    total = max(35.0, total)
    max_coverage = round(weekly_earnings * 0.85, 2)
    return {
        "base_premium": base,
        "earnings_linked": earnings_linked,
        "zone_risk_loading": zone_risk_loading,
        "claims_surcharge": claims_surcharge,
        "total_premium": total,
        "max_coverage": max_coverage,
    }


def get_prior_claims_count(worker_id: str, db: Session) -> int:
    """Count claims this month for surcharge calculation."""
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return (
        db.query(Claim)
        .join(Policy, Claim.policy_id == Policy.id)
        .filter(and_(Policy.worker_id == worker_id, Claim.created_at >= start_of_month))
        .count()
    )
