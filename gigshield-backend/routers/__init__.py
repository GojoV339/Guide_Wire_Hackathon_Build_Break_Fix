from routers.auth import router as auth_router
from routers.workers import router as workers_router
from routers.policies import router as policies_router
from routers.claims import router as claims_router
from routers.payouts import router as payouts_router

__all__ = [
    "auth_router",
    "workers_router",
    "policies_router",
    "claims_router",
    "payouts_router",
]

