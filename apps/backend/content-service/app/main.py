"""
SkillForge AI - Content Service
FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import uvicorn
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI Content Service...")

    try:
        # Initialize database
        from app.core.database import init_db
        await init_db()
        logger.info("✓ Database initialized")

        # Test Redis connection
        from app.core.cache import get_redis
        redis_client = await get_redis()
        await redis_client.ping()
        logger.info("✓ Redis connection established")

        logger.info("🚀 Content Service started successfully")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down SkillForge AI Content Service...")
    try:
        from app.core.cache import close_redis
        await close_redis()
        logger.info("✓ Redis connection closed")
        logger.info("🔄 Content Service shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - Content Service",
    description="Microservice for Content management in SkillForge AI platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Add security middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Add API Gateway integration headers
    if settings.API_GATEWAY_URL:
        response.headers["X-API-Gateway"] = settings.API_GATEWAY_URL
    response.headers["X-Service-Name"] = "content-service"
    
    return response


# Include API routers
from app.api.v1.content import router as content_router

app.include_router(
    content_router,
    prefix=f"{settings.API_V1_STR}/content",
    tags=["content"]
)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "skillforge-ai-content-service",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "api_gateway": settings.API_GATEWAY_URL
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Test database connection
        from app.core.database import get_db
        db = await anext(get_db())
        await db.execute(text("SELECT 1"))

        # Test Redis connection
        from app.core.cache import get_redis
        redis_client = await get_redis()
        await redis_client.ping()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "content-service",
            "version": "1.0.0",
            "api_gateway": settings.API_GATEWAY_URL,
            "checks": {
                "database": "✓ Connected",
                "redis": "✓ Connected"
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "service": "content-service",
                "error": str(e)
            }
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )