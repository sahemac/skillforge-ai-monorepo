"""
SkillForge AI - Payment Service
FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import create_db_and_tables, get_db_health
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI Payment Service...")

    # Initialize database
    try:
        await create_db_and_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't fail startup - let health checks handle it

    yield

    # Shutdown
    logger.info("Shutting down SkillForge AI Payment Service...")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - Payment Service",
    description="Microservice for Payment processing in SkillForge AI platform",
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
    response.headers["X-Service-Name"] = "payment-service"
    
    return response


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "skillforge-ai-payment_service-service",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "api_gateway": settings.API_GATEWAY_URL
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    # Check database health
    db_health = await get_db_health()

    overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "service": "payment-service",
        "version": "1.0.0",
        "api_gateway": settings.API_GATEWAY_URL,
        "components": {
            "database": db_health,
            "stripe": {"status": "healthy" if settings.STRIPE_SECRET_KEY else "not_configured"},
            "paypal": {"status": "healthy" if settings.PAYPAL_CLIENT_ID else "not_configured"},
        }
    }


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