"""
API v1 router for SkillForge AI Project Service
"""

from fastapi import APIRouter
from .deliverables import router as deliverables_router

api_router = APIRouter()

# Include deliverables routes
api_router.include_router(deliverables_router, prefix="/api/v1")

@api_router.get("/projects")
async def list_projects():
    """List projects."""
    return {"projects": []}

@api_router.post("/projects")
async def create_project():
    """Create new project."""
    return {"message": "Project created"}

@api_router.get("/milestones")
async def list_milestones():
    """List project milestones."""
    return {"milestones": []}

@api_router.post("/milestones")
async def create_milestone():
    """Create new milestone."""
    return {"message": "Milestone created"}