import os
from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.worker import Worker
from schemas.worker import OTPRequest
from schemas.worker import OTPVerify
from schemas.worker import TokenResponse
from services.auth_service import create_access_token
from services.auth_service import generate_otp
from services.auth_service import get_current_worker
from services.sms_service import send_otp_sms

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/send-otp")
def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP to worker phone number. Creates worker if not exists."""
    worker = db.query(Worker).filter(Worker.phone_number == request.phone_number).first()

    if not worker:
        worker = Worker(phone_number=request.phone_number)
        db.add(worker)

    otp = generate_otp()
    worker.otp = otp
    worker.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    sms_ok, sms_err = send_otp_sms(request.phone_number, otp)
    env = os.getenv("ENVIRONMENT", "development")

    if sms_ok:
        print(f"[AUTH] OTP SMS sent to {request.phone_number}")
        return {"message": "OTP sent successfully", "phone": request.phone_number}

    print(f"[AUTH] SMS failed for {request.phone_number}: {sms_err}")

    if env == "development":
        return {
            "message": "OTP sent (dev fallback: SMS failed or not configured)",
            "phone": request.phone_number,
            "otp": otp,
            "dev_note": sms_err,
        }

    raise HTTPException(
        status_code=503,
        detail=f"Could not send SMS. Configure SMS_PROVIDER and credentials. ({sms_err})",
    )


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and return JWT access token."""
    worker = db.query(Worker).filter(Worker.phone_number == request.phone_number).first()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    if not worker.otp or worker.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if worker.otp_expires_at and datetime.utcnow() > worker.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")

    worker.otp = None
    worker.otp_expires_at = None
    db.commit()

    token = create_access_token(worker.id)
    return TokenResponse(access_token=token, worker_id=worker.id)


@router.get("/me")
def get_me(current_worker: Worker = Depends(get_current_worker)):
    """Get current authenticated worker profile."""
    return {
        "id": current_worker.id,
        "phone_number": current_worker.phone_number,
        "name": current_worker.name,
        "home_zone_pincode": current_worker.home_zone_pincode,
        "risk_score": current_worker.risk_score,
    }
