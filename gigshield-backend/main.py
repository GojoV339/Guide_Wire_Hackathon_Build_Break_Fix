import os

from dotenv import load_dotenv
load_dotenv("config.env", override=True) # Load the newly created config file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base
from database import engine
from jobs.trigger_monitor import start_scheduler
from routers import analytics
from routers import auth
from routers import claims
from routers import payouts
from routers import policies
from routers import workers

app = FastAPI(
    title="GigShield API",
    version="2.0.0",
    description="Parametric income insurance for gig delivery workers",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(payouts.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Database tables created")
    start_scheduler()
    print("[STARTUP] GigShield API v2.0 running")


@app.get("/")
def health_check():
    return {
        "status": "GigShield API is running",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "ai_powered": True,
    }
