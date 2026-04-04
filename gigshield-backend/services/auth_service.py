import os
import random
from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.orm import Session

from database import get_db
from models.worker import Worker

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

security = HTTPBearer()


def generate_otp() -> str:
    """Generate a 4-digit OTP."""
    return str(random.randint(1000, 9999))


def create_access_token(worker_id: str) -> str:
    """Create JWT access token for a worker."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": worker_id, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_worker(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Worker:
    """Get current worker from JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        worker_id = payload.get("sub")
        if not worker_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=401, detail="Worker not found")
        return worker
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
