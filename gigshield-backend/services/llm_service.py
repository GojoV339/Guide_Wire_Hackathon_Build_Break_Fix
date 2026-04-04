import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv("config.env", override=True)

_api_key = os.getenv("GROQ_API_KEY") or ""
_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
client = Groq(api_key=_api_key) if _api_key else None


def _strip_json_fenced(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lstrip().startswith("json"):
                inner = inner.lstrip()[4:]
            return inner.strip()
    return text


def _parse_json_response(text: str) -> dict:
    cleaned = _strip_json_fenced(text)
    return json.loads(cleaned)


def _chat_json(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """Call Groq chat completions; return assistant message text."""
    if not client:
        raise RuntimeError("GROQ_API_KEY not configured")
    response = client.chat.completions.create(
        model=_model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def calculate_risk_score_llm(
    zone_pincode: str,
    zone_name: str,
    recent_disruptions_count: int,
    season: str,
) -> dict:
    """Call Groq-hosted model to calculate insurance risk score for a delivery zone."""
    print(f"[LLM/Groq] Calculating risk score for zone {zone_pincode} {zone_name}")
    if not client:
        return {
            "risk_score": 5.0,
            "risk_category": "medium",
            "reasoning": "GROQ_API_KEY not configured; default score assigned",
        }
    system_prompt = (
        "You are an insurance actuary for parametric income insurance for gig delivery workers in India. "
        "Respond with valid JSON only. No text outside JSON."
    )
    user_prompt = f"""Calculate risk score for this delivery zone in Bengaluru India:

Zone pincode: {zone_pincode}
Zone name: {zone_name}
Recent disruptions in last 90 days: {recent_disruptions_count}
Current season: {season}

Return JSON with exactly these fields:
{{
  "risk_score": <number 1.0 to 10.0>,
  "risk_category": <"low" or "medium" or "high">,
  "reasoning": <one sentence why>
}}

Consider flood risk, monsoon impact, and civic unrest for Bengaluru zones."""
    try:
        text = _chat_json(system_prompt, user_prompt, max_tokens=500)
        return _parse_json_response(text)
    except Exception as e:
        print(f"[LLM ERROR] Risk score failed: {e}")
        return {
            "risk_score": 5.0,
            "risk_category": "medium",
            "reasoning": "Default score assigned",
        }


def analyze_fraud_llm(
    event_type: str,
    event_severity: float,
    zone_pincode: str,
    claims_last_7_days: int,
    policy_created_before_event: bool,
    event_verified_by_api: bool,
    is_duplicate: bool,
    days_as_customer: int,
) -> dict:
    """Call Groq-hosted model to analyze a claim for fraud signals."""
    print(f"[LLM/Groq] Analyzing fraud for {event_type} claim in zone {zone_pincode}")
    if not client:
        return {
            "trust_score": 0.70,
            "decision": "manual_review",
            "fraud_indicators": ["GROQ_API_KEY not configured"],
            "genuine_indicators": [],
            "reasoning": "Defaulted to manual review (no LLM client)",
        }
    system_prompt = (
        "You are a fraud detection specialist for parametric insurance for gig workers in India. "
        "Respond with valid JSON only. No text outside JSON."
    )
    user_prompt = f"""Analyze this insurance claim for fraud:

Event type: {event_type}
Severity: {event_severity}
Zone: {zone_pincode}
Worker claims in last 7 days: {claims_last_7_days}
Policy existed before event: {policy_created_before_event}
Event confirmed by API: {event_verified_by_api}
Is duplicate claim: {is_duplicate}
Days as customer: {days_as_customer}

Return JSON with exactly these fields:
{{
  "trust_score": <number 0.0 to 1.0>,
  "decision": <"auto_approve" or "manual_review" or "reject">,
  "fraud_indicators": [<list of suspicious signals found>],
  "genuine_indicators": [<list of signals supporting legitimacy>],
  "reasoning": <one sentence explanation>
}}

Rules:
- is_duplicate=true means always reject
- policy_created_before_event=false is major red flag
- claims_last_7_days > 3 is suspicious
- auto_approve requires trust_score >= 0.85
- reject requires trust_score < 0.40 or is_duplicate=true"""
    try:
        text = _chat_json(system_prompt, user_prompt, max_tokens=600)
        return _parse_json_response(text)
    except Exception as e:
        print(f"[LLM ERROR] Fraud analysis failed: {e}")
        return {
            "trust_score": 0.70,
            "decision": "manual_review",
            "fraud_indicators": ["analysis unavailable"],
            "genuine_indicators": [],
            "reasoning": "Defaulted to manual review due to analysis error",
        }


def calculate_payout_llm(
    event_type: str,
    event_severity: float,
    duration_hours: float,
    daily_earnings: float,
    coverage_remaining: float,
) -> dict:
    """Call Groq-hosted model to calculate exact payout amount."""
    print(f"[LLM/Groq] Calculating payout for {event_type} {duration_hours}hrs")
    if not client:
        hourly = daily_earnings / 8
        rates = {"rain": 0.80, "aqi": 0.60, "heat": 0.50, "curfew": 0.90, "app_outage": 0.70}
        rate = rates.get(event_type, 0.60)
        calculated = duration_hours * hourly * rate
        final = min(calculated, coverage_remaining)
        return {
            "hourly_rate": hourly,
            "coverage_rate_percent": rate * 100,
            "calculated_amount": calculated,
            "final_payout": final,
            "calculation_explanation": f"{duration_hours}hrs x Rs{hourly:.1f} x {rate*100:.0f}% = Rs{calculated:.2f} (fallback)",
        }
    system_prompt = (
        "You are an insurance claims adjuster for parametric insurance for gig workers in India. "
        "Respond with valid JSON only. No text outside JSON."
    )
    user_prompt = f"""Calculate insurance payout:

Event type: {event_type}
Severity: {event_severity}
Duration hours: {duration_hours}
Daily earnings: Rs {daily_earnings}
Coverage remaining: Rs {coverage_remaining}

Coverage rates:
rain=80%, aqi=60%, heat=50%, curfew=90%, app_outage=70%
Hourly rate = daily_earnings / 8

Return JSON with exactly these fields:
{{
  "hourly_rate": <number>,
  "coverage_rate_percent": <number>,
  "calculated_amount": <number>,
  "final_payout": <number capped at coverage_remaining>,
  "calculation_explanation": <string showing math e.g. "2hrs x Rs87.5 x 80% = Rs140">
}}"""
    try:
        text = _chat_json(system_prompt, user_prompt, max_tokens=400)
        return _parse_json_response(text)
    except Exception as e:
        print(f"[LLM ERROR] Payout calculation failed: {e}")
        hourly = daily_earnings / 8
        rates = {
            "rain": 0.80,
            "aqi": 0.60,
            "heat": 0.50,
            "curfew": 0.90,
            "app_outage": 0.70,
        }
        rate = rates.get(event_type, 0.60)
        calculated = duration_hours * hourly * rate
        final = min(calculated, coverage_remaining)
        return {
            "hourly_rate": hourly,
            "coverage_rate_percent": rate * 100,
            "calculated_amount": calculated,
            "final_payout": final,
            "calculation_explanation": f"{duration_hours}hrs x Rs{hourly:.1f} x {rate*100:.0f}% = Rs{calculated:.2f}",
        }


def get_forecast_llm(
    city: str,
    active_pincodes: list,
    season: str,
    recent_claim_types: list,
) -> dict:
    """Call Groq-hosted model to generate weekly forecast for insurer dashboard."""
    print(f"[LLM/Groq] Generating weekly forecast for {city}")
    if not client:
        return {
            "predicted_min_inr": 50000,
            "predicted_max_inr": 100000,
            "high_risk_zones": active_pincodes[:2] if active_pincodes else [],
            "primary_threat": "Heavy rainfall expected",
            "reserve_recommendation_inr": 120000,
            "reasoning": "Default forecast (GROQ_API_KEY not configured)",
        }
    system_prompt = (
        "You are an insurance analytics specialist. Respond with valid JSON only. No text outside JSON."
    )
    user_prompt = f"""Generate weekly insurance forecast:

City: {city}
Active zones: {active_pincodes}
Season: {season}
Recent claim types: {recent_claim_types}

Assume average policy Rs4200 and average claim Rs300.

Return JSON:
{{
  "predicted_min_inr": <number>,
  "predicted_max_inr": <number>,
  "high_risk_zones": [<pincodes from active list>],
  "primary_threat": <string>,
  "reserve_recommendation_inr": <number>,
  "reasoning": <one sentence>
}}"""
    try:
        text = _chat_json(system_prompt, user_prompt, max_tokens=500)
        return _parse_json_response(text)
    except Exception as e:
        print(f"[LLM ERROR] Forecast failed: {e}")
        return {
            "predicted_min_inr": 50000,
            "predicted_max_inr": 100000,
            "high_risk_zones": active_pincodes[:2] if active_pincodes else [],
            "primary_threat": "Heavy rainfall expected",
            "reserve_recommendation_inr": 120000,
            "reasoning": "Default forecast due to analysis error",
        }
