"""
API v1 endpoints for SkillForge AI Company Service
"""

from .companies import router as companies_router

__all__ = ["companies_router"]