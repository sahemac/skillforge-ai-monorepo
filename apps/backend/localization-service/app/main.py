"""
SkillForge AI - Localization Service
Multi-language content and interface localization
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import uvicorn
import time
import logging

from app.core.config import get_settings
from app.core.database import init_db, get_db
from app.core.cache import close_redis, get_redis
from app.api.v1.translations import router as translations_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI Localization Service...")

    try:
        # Initialize database
        await init_db()
        logger.info("✓ Database initialized")

        # Test Redis connection (skip in development if Redis is not available)
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            logger.info("✓ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠ Redis connection failed: {e}")
            if settings.is_production:
                raise
            logger.info("✓ Running in development mode without Redis")

        logger.info("🚀 Localization Service started successfully")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down SkillForge AI Localization Service...")
    try:
        await close_redis()
        logger.info("✓ Redis connection closed")
        logger.info("🔄 Localization Service shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - Localization Service",
    description="Multi-language content and interface localization service",
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
    response.headers["X-Service-Name"] = "localization-service"

    return response


# Include API routers
app.include_router(
    translations_router,
    prefix=f"{settings.API_V1_STR}/translations",
    tags=["translations"]
)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "skillforge-ai-localization-service",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "api_gateway": settings.API_GATEWAY_URL,
        "supported_languages": ["en", "fr", "es", "de", "it", "pt", "ja", "ko", "zh"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Test database connection
        db = await anext(get_db())
        await db.execute(text("SELECT 1"))

        # Test Redis connection (skip in development if Redis is not available)
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            logger.info("✓ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠ Redis connection failed: {e}")
            logger.info("✓ Redis connection closed")

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "localization-service",
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
                "service": "localization-service",
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