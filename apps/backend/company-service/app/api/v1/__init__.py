"""
API v1 router for SkillForge AI Company Service
"""

from fastapi import APIRouter

from app.api.v1.endpoints import companies_router

api_router = APIRouter()

# Include routers
api_router.include_router(
    companies_router,
    prefix="/companies",
    tags=["companies"]
)

__all__ = ["api_router"]