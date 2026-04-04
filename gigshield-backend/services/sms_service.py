"""Send OTP via SMS. Configure one provider in .env (Twilio or Fast2SMS)."""

import base64
import os
from typing import Optional
from typing import Tuple

import httpx

from dotenv import load_dotenv

load_dotenv()


def _normalize_10_digit(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        return digits[2:]
    if len(digits) == 10:
        return digits
    raise ValueError("Expected 10-digit Indian mobile number")


def _e164_in(phone_10: str) -> str:
    return f"+91{phone_10}"


def send_otp_sms(phone_number: str, otp: str) -> Tuple[bool, Optional[str]]:
    """
    Send OTP SMS. Returns (success, error_message).
    If SMS_PROVIDER is unset or 'none', does not send (caller may use dev fallback).
    """
    provider = (os.getenv("SMS_PROVIDER") or "none").strip().lower()
    try:
        phone_10 = _normalize_10_digit(phone_number)
    except ValueError as e:
        return False, str(e)

    body = f"Your GigShield OTP is {otp}. Valid for 10 minutes. Do not share."

    if provider in ("", "none"):
        return False, "SMS_PROVIDER not set (use twilio or fast2sms)"

    if provider == "twilio":
        return _send_twilio(phone_10, body)

    if provider == "fast2sms":
        return _send_fast2sms(phone_10, body)

    return False, f"Unknown SMS_PROVIDER: {provider}"


def _send_twilio(phone_10: str, body: str) -> Tuple[bool, Optional[str]]:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_num = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
    if not all([account_sid, auth_token, from_num]):
        return False, "Twilio env vars incomplete (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)"

    auth = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    to_e164 = _e164_in(phone_10)

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                url,
                data={"To": to_e164, "From": from_num, "Body": body},
                headers={"Authorization": f"Basic {auth}"},
            )
    except httpx.HTTPError as e:
        return False, str(e)

    if r.status_code == 201:
        return True, None
    return False, r.text[:500]


def _send_fast2sms(phone_10: str, body: str) -> Tuple[bool, Optional[str]]:
    api_key = os.getenv("FAST2SMS_API_KEY", "").strip()
    if not api_key:
        return False, "FAST2SMS_API_KEY not set"

    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "route": "q",
        "message": body,
        "language": "english",
        "flash": 0,
        "numbers": phone_10,
    }
    headers = {"authorization": api_key, "Content-Type": "application/json"}

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as e:
        return False, str(e)

    try:
        data = r.json()
    except Exception:
        return False, r.text[:500]

    if r.status_code == 200 and data.get("return") is True:
        return True, None
    return False, str(data)[:500]
