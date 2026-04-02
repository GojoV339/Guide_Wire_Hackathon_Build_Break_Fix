import os
import random
from datetime import datetime
from datetime import timedelta
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.orm import Session

from database import get_db
from models.worker import Worker

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "change-me"
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or "10080")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-otp")


def generate_otp() -> str:
    otp = str(random.randint(1000, 9999))
    return otp


def create_access_token(data: dict) -> str:
    to_encode = dict(data)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def get_current_worker(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Worker:
    payload = verify_token(token)
    worker_id = payload.get("worker_id")
    if not worker_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker not found")
    return worker

