import datetime
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from database import get_db
from models.worker import Worker
from schemas.worker import OTPRequest
from schemas.worker import OTPVerify
from schemas.worker import TokenResponse
from services.auth_service import create_access_token
from services.auth_service import generate_otp
from services.auth_service import get_current_worker

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT") or "development"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(payload: OTPRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Send a 4-digit OTP to a worker phone number (dev returns OTP in response)."""
    try:
        worker = db.query(Worker).filter(Worker.phone_number == payload.phone_number).first()
        if not worker:
            worker = Worker(
                phone_number=payload.phone_number,
                home_zone_pincode="000000",
                daily_earnings_declared=0.0,
            )
            db.add(worker)
            db.commit()
            db.refresh(worker)

        otp = generate_otp()
        worker.otp = otp
        worker.otp_expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        db.add(worker)
        db.commit()

        response: dict[str, Any] = {"message": "OTP sent successfully"}
        if ENVIRONMENT == "development":
            response["otp"] = otp
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)) -> TokenResponse:
    """Verify OTP and return a JWT access token if valid."""
    try:
        worker = db.query(Worker).filter(Worker.phone_number == payload.phone_number).first()
        if not worker:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

        if not worker.otp or not worker.otp_expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not requested")

        if datetime.datetime.utcnow() > worker.otp_expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

        if worker.otp != payload.otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

        token = create_access_token({"worker_id": worker.id})
        worker.otp = None
        worker.otp_expires_at = None
        db.add(worker)
        db.commit()

        return TokenResponse(access_token=token, token_type="bearer", worker_id=worker.id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify OTP: {e}")


@router.get("/me", status_code=status.HTTP_200_OK)
def me(current_worker: Worker = Depends(get_current_worker)) -> dict[str, Any]:
    """Return the authenticated worker profile."""
    return {
        "id": current_worker.id,
        "phone_number": current_worker.phone_number,
        "name": current_worker.name,
        "aadhaar_verified": current_worker.aadhaar_verified,
        "platform_partner_id": current_worker.platform_partner_id,
        "home_zone_pincode": current_worker.home_zone_pincode,
        "daily_earnings_declared": current_worker.daily_earnings_declared,
        "upi_id": current_worker.upi_id,
        "risk_score": current_worker.risk_score,
        "is_active": current_worker.is_active,
        "created_at": current_worker.created_at,
        "updated_at": current_worker.updated_at,
    }

