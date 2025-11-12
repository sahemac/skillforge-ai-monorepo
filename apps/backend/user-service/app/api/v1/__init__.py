"""
API v1 router for SkillForge AI User Service
"""

from fastapi import APIRouter

from .endpoints import users_router

# Create API router
api_router = APIRouter()

# Authentication functionality has been moved to auth-service
# Auth routes (/auth/register, /auth/login, etc.) are now handled
# by the dedicated auth-service microservice
# Migration date: 2025-11-07
# Clients should now call auth-service directly or via API Gateway

# Include endpoint routers with prefixes and tags
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)

# Company functionality has been moved to company-service
# api_router.include_router(
#     companies_router,
#     prefix="/companies",
#     tags=["companies"],
# )

__all__ = ["api_router"]