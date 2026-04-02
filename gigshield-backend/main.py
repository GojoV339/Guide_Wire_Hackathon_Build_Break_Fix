import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base
from database import engine
from jobs.trigger_monitor import start_scheduler
from routers.auth import router as auth_router
from routers.claims import router as claims_router
from routers.payouts import router as payouts_router
from routers.policies import router as policies_router
from routers.workers import router as workers_router

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT") or "development"

app = FastAPI(
    title="GigShield API",
    version="1.0.0",
    description="Parametric income insurance for gig workers",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workers_router)
app.include_router(policies_router)
app.include_router(claims_router)
app.include_router(payouts_router)

scheduler = None


@app.on_event("startup")
def on_startup() -> None:
    global scheduler
    Base.metadata.create_all(bind=engine)
    scheduler = start_scheduler()


@app.get("/", tags=["health"])
def health() -> dict:
    """Health check route to verify API is up and show environment."""
    return {
        "status": "GigShield API is running",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
    }

