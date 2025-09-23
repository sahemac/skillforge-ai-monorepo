"""
Main FastAPI application for Project Service
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import check_db_connection
from app.api.v1.deliverables import router as deliverables_router

settings = get_settings()

app = FastAPI(
    title="SkillForge Project Service",
    description="Service de gestion des projets et livrables SkillForge AI",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(deliverables_router, prefix="/api/v1", tags=["deliverables"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = await check_db_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "project-service",
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SkillForge Project Service",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )