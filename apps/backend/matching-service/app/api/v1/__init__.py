"""
API v1 router for SkillForge AI Matching Service
"""

from fastapi import APIRouter

from .endpoints import matching, preferences, recommendations

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    matching.router,
    prefix="/matching",
    tags=["matching"]
)

api_router.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["preferences"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"]
)