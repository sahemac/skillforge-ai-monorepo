"""
API v1 router for SkillForge AI User Service
"""

from fastapi import APIRouter

from .endpoints import auth_router, users_router, companies_router

# Create API router
api_router = APIRouter()

# Include endpoint routers with prefixes and tags
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    companies_router,
    prefix="/companies", 
    tags=["companies"],
)

__all__ = ["api_router"]