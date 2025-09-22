"""
SkillForge AI - Scheduling-service
FastAPI application entry point for Session and training scheduling management
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi.errors import RateLimitExceeded
import uvicorn
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import create_db_and_tables, check_db_connection
from app.core.cache import initialize_cache, shutdown_cache, cache_service
from app.core.rate_limiting import limiter, rate_limit_exceeded_handler
from app.core.monitoring import (
    PrometheusMiddleware, 
    get_metrics, 
    get_metrics_content_type,
    MetricsCollector
)
from app.core.iap_middleware import IAPMiddleware
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI Scheduling-service...")
    
    # Initialize database
    await create_db_and_tables()
    logger.info("Database tables created/verified")
    
    # Initialize cache (Redis)
    cache_connected = await initialize_cache()
    if cache_connected:
        logger.info("Redis cache initialized successfully")
    else:
        logger.warning("Redis cache not available - running without cache")
    
    logger.info("Scheduling-service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillForge AI Scheduling-service...")
    await shutdown_cache()
    logger.info("Services shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - Scheduling-service",
    description="Session and training scheduling management",
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

# Add IAP middleware
app.add_middleware(
    IAPMiddleware,
    project_number="584748485117",
    backend_service_id="scheduling-service-backend-staging"
)

# Add Prometheus monitoring middleware
if settings.ENABLE_METRICS:
    app.add_middleware(PrometheusMiddleware)

# Add rate limiting
app.state.limiter = limiter
app.state.environment = settings.ENVIRONMENT
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "skillforge-ai-scheduling-service",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "description": "Session and training scheduling management"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    db_healthy = await check_db_connection()
    cache_status = "healthy" if cache_service.is_connected else "unavailable"
    status = "healthy" if db_healthy else "unhealthy"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "service": "scheduling-service",
        "version": "1.0.0",
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
            "cache": cache_status,
            "metrics": "enabled" if settings.ENABLE_METRICS else "disabled"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.ENABLE_METRICS:
        return JSONResponse(status_code=404, content={"error": "Metrics disabled"})
    
    await MetricsCollector.collect_all()
    return PlainTextResponse(content=get_metrics(), media_type=get_metrics_content_type())


@app.get("/cache/info")
async def cache_info():
    """Cache information endpoint (admin only)."""
    return await cache_service.info()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error", "detail": str(exc)})


app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == "development", log_level="info")
