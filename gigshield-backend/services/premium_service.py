import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.claim import Claim
from models.disruption import DisruptionEvent


def calculate_risk_score(zone_pincode: str, db: Session) -> float:
    since = datetime.datetime.utcnow() - datetime.timedelta(days=90)
    count = (
        db.query(DisruptionEvent)
        .filter(and_(DisruptionEvent.zone_pincode == zone_pincode, DisruptionEvent.created_at >= since))
        .count()
    )

    base_score = 3.0
    increments = (count // 2) * 0.5
    score = base_score + increments
    return min(9.0, float(score))


def calculate_weekly_premium(daily_earnings: float, risk_score: float, prior_claims_this_month: int) -> dict:
    base_premium = 29.0
    weekly_earnings = daily_earnings * 7
    earnings_linked = weekly_earnings * 0.014
    zone_risk_loading = risk_score * 1.5
    claims_surcharge = prior_claims_this_month * 4.0
    total_premium = base_premium + earnings_linked + zone_risk_loading + claims_surcharge
    max_coverage = weekly_earnings * 0.85

    return {
        "base_premium": base_premium,
        "weekly_earnings": weekly_earnings,
        "earnings_linked": earnings_linked,
        "risk_score": risk_score,
        "zone_risk_loading": zone_risk_loading,
        "claims_surcharge": claims_surcharge,
        "total_premium": total_premium,
        "max_coverage": max_coverage,
    }


def calculate_payout_amount(
    event_type: str,
    duration_hours: float,
    daily_earnings: float,
    coverage_remaining: float,
) -> float:
    hourly_rate = daily_earnings / 8
    coverage_rates = {
        "rain": 0.80,
        "aqi": 0.60,
        "heat": 0.50,
        "curfew": 0.90,
        "app_outage": 0.70,
    }
    rate = coverage_rates.get(event_type, 0.60)
    calculated = duration_hours * hourly_rate * rate
    return float(min(calculated, coverage_remaining))

