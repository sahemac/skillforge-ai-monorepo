"""
API v1 routes
"""

from fastapi import APIRouter

from .notifications import router as notifications_router
from .templates import router as templates_router
from .preferences import router as preferences_router

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    notifications_router,
    prefix="/notifications",
    tags=["notifications"]
)

api_router.include_router(
    templates_router,
    prefix="/templates",
    tags=["templates"]
)

api_router.include_router(
    preferences_router,
    prefix="/preferences",
    tags=["preferences"]
)