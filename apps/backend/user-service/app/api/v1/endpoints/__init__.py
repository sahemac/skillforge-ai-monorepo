"""
API endpoints for SkillForge AI User Service v1
"""

from .users import router as users_router

# Authentication functionality has been moved to auth-service
# Auth routes are now handled by the dedicated auth-service microservice
# Migration date: 2025-11-07
# from .auth import router as auth_router

# Company functionality has been moved to company-service
# from .companies import router as companies_router

__all__ = [
    "users_router",
]