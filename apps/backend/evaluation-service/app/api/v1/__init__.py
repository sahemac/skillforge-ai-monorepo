"""
API v1 router for AI Orchestrator Service
"""

from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/agents")
async def list_agents():
    """List AI agents."""
    return {"agents": []}

@api_router.post("/agents")
async def create_agent():
    """Create new AI agent."""
    return {"message": "Agent created"}

@api_router.get("/tasks")
async def list_tasks():
    """List AI tasks."""
    return {"tasks": []}

@api_router.post("/tasks")
async def create_task():
    """Create new AI task."""
    return {"message": "Task created"}