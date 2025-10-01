"""
API v1 package
"""

from fastapi import APIRouter

from .endpoints import payments, subscriptions

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(payments.router)
api_router.include_router(subscriptions.router)

__all__ = ["api_router"]