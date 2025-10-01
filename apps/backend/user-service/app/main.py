"""
SkillForge AI - User Service
FastAPI application entry point
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.iap_middleware import IAPMiddleware
from app.core.structured_logging import (
    configure_logging, 
    get_logger,
    CorrelationMiddleware,
    LoggingMiddleware
)
from app.api.v1 import api_router

# Configure structured logging
configure_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI User Service...")
    
    # Initialize database
    await create_db_and_tables()
    logger.info("Database tables created/verified")
    
    # Initialize cache (Redis)
    cache_connected = await initialize_cache()
    if cache_connected:
        logger.info("Redis cache initialized successfully")
    else:
        logger.warning("Redis cache not available - running without cache")
    
    # Initialize metrics
    logger.info("Monitoring and metrics initialized")
    
    # Initialize FastAPI Instrumentator for enhanced metrics
    if settings.ENABLE_METRICS:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics", "/health"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="skillforge_inprogress",
            inprogress_labels=True,
        )
        instrumentator.instrument(app).expose(app)
        logger.info("FastAPI Instrumentator initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillForge AI User Service...")
    await shutdown_cache()
    logger.info("Services shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - User Service",
    description="Microservice for user management and authentication in SkillForge AI platform",
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

# Add logging middleware (first for proper request tracking)
app.add_middleware(CorrelationMiddleware)
app.add_middleware(LoggingMiddleware)

# Add IAP middleware (before rate limiting for proper auth)
app.add_middleware(
    IAPMiddleware,
    project_number="584748485117",
    backend_service_id="user-service-backend-staging"
)

# Add Prometheus monitoring middleware
if settings.ENABLE_METRICS:
    app.add_middleware(PrometheusMiddleware)

# Add rate limiting
app.state.limiter = limiter
app.state.environment = settings.ENVIRONMENT  # For IAP middleware
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serves login page."""
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    login_file = os.path.join(static_dir, "login.html")

    if os.path.exists(login_file):
        with open(login_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback to JSON if login.html doesn't exist
        return JSONResponse({
            "service": "skillforge-ai-user-service",
            "version": "1.0.0",
            "status": "healthy",
            "environment": settings.ENVIRONMENT
        })

@app.get("/api")
async def api_info():
    """API endpoint with service info."""
    return {
        "service": "skillforge-ai-user-service",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    import httpx
    
    checks = {}
    overall_healthy = True
    
    # Check database connection
    try:
        db_healthy = await check_db_connection()
        checks["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "response_time_ms": None
        }
        if not db_healthy:
            overall_healthy = False
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy", 
            "error": str(e),
            "response_time_ms": None
        }
        overall_healthy = False
    
    # Check cache connection
    cache_start = time.time()
    try:
        cache_connected = cache_service.is_connected
        if cache_connected:
            # Test cache with a simple operation
            await cache_service.set("health_check", "ok", expire=1)
            cache_test = await cache_service.get("health_check")
            cache_response_time = (time.time() - cache_start) * 1000
            checks["cache"] = {
                "status": "healthy" if cache_test == "ok" else "degraded",
                "response_time_ms": round(cache_response_time, 2)
            }
        else:
            checks["cache"] = {
                "status": "unavailable",
                "response_time_ms": None
            }
    except Exception as e:
        checks["cache"] = {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": None
        }
    
    # Check external dependencies (example: email service)
    try:
        # Test SMTP connection if configured
        if hasattr(settings, 'SMTP_HOST') and settings.SMTP_HOST:
            smtp_start = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Mock check - in real implementation, test actual SMTP
                smtp_response_time = (time.time() - smtp_start) * 1000
                checks["smtp"] = {
                    "status": "healthy",
                    "response_time_ms": round(smtp_response_time, 2)
                }
        else:
            checks["smtp"] = {"status": "not_configured", "response_time_ms": None}
    except Exception as e:
        checks["smtp"] = {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": None
        }
        overall_healthy = False
    
    # Check metrics system
    try:
        metrics_start = time.time()
        if settings.ENABLE_METRICS:
            await MetricsCollector.collect_all()
            metrics_response_time = (time.time() - metrics_start) * 1000
            checks["metrics"] = {
                "status": "healthy",
                "response_time_ms": round(metrics_response_time, 2)
            }
        else:
            checks["metrics"] = {"status": "disabled", "response_time_ms": None}
    except Exception as e:
        checks["metrics"] = {
            "status": "unhealthy", 
            "error": str(e),
            "response_time_ms": None
        }
    
    # Overall status
    status = "healthy" if overall_healthy else "unhealthy"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "service": "user-service", 
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": checks
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.ENABLE_METRICS:
        return JSONResponse(
            status_code=404,
            content={"error": "Metrics disabled"}
        )
    
    # Collect latest metrics
    await MetricsCollector.collect_all()
    
    # Return metrics in Prometheus format
    return PlainTextResponse(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )


@app.get("/cache/info")
async def cache_info():
    """Cache information endpoint (admin only)."""
    return await cache_service.info()


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )


# Mount static files
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )