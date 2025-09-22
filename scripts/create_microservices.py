#!/usr/bin/env python3
"""
Script to create all 22 missing backend services for SkillForge AI
Based on the existing user-service structure
"""

import os
import json

# Base directory for backend services
BACKEND_DIR = "C:\\Users\\DELL\\Documents\\GitHub\\skillforge-ai-monorepo\\apps\\backend"

# Service definitions with their specific configurations
SERVICES = [
    {
        "name": "ai-orchestrator-service",
        "port": 8001,
        "description": "Microservice for AI agent coordination and orchestration in SkillForge AI platform",
        "database": "skillforge_ai_orchestrator",
        "specific_deps": ["openai", "langchain"],
        "endpoints": ["agents", "orchestration", "workflows"]
    },
    {
        "name": "chat-messaging-service", 
        "port": 8002,
        "description": "Microservice for real-time chat and messaging in SkillForge AI platform",
        "database": "skillforge_chat",
        "specific_deps": ["websockets", "channels"],
        "endpoints": ["chats", "messages", "channels"]
    },
    {
        "name": "recommendation-service",
        "port": 8003, 
        "description": "Microservice for recommendation engine in SkillForge AI platform",
        "database": "skillforge_recommendations",
        "specific_deps": ["scikit-learn", "numpy"],
        "endpoints": ["recommendations", "algorithms", "preferences"]
    },
    {
        "name": "scheduling-service",
        "port": 8004,
        "description": "Microservice for scheduling sessions and training in SkillForge AI platform", 
        "database": "skillforge_scheduling",
        "specific_deps": ["croniter", "pytz"],
        "endpoints": ["schedules", "sessions", "bookings"]
    },
    {
        "name": "evaluation-service",
        "port": 8005,
        "description": "Microservice for 360-degree evaluation system in SkillForge AI platform",
        "database": "skillforge_evaluations", 
        "specific_deps": ["pandas", "matplotlib"],
        "endpoints": ["evaluations", "assessments", "feedback"]
    },
    {
        "name": "matching-service",
        "port": 8006,
        "description": "Microservice for matching algorithms in SkillForge AI platform",
        "database": "skillforge_matching",
        "specific_deps": ["networkx", "scipy"],
        "endpoints": ["matches", "algorithms", "compatibility"]
    },
    {
        "name": "project-service", 
        "port": 8007,
        "description": "Microservice for project management in SkillForge AI platform",
        "database": "skillforge_projects",
        "specific_deps": ["gitpython"],
        "endpoints": ["projects", "tasks", "milestones"]
    },
    {
        "name": "portfolio-service",
        "port": 8008,
        "description": "Microservice for user portfolios in SkillForge AI platform", 
        "database": "skillforge_portfolios",
        "specific_deps": ["pillow"],
        "endpoints": ["portfolios", "artifacts", "showcases"]
    },
    {
        "name": "gamification-service",
        "port": 8009,
        "description": "Microservice for gamification system in SkillForge AI platform",
        "database": "skillforge_gamification",
        "specific_deps": [],
        "endpoints": ["achievements", "badges", "leaderboards"]
    },
    {
        "name": "localization-service",
        "port": 8010,
        "description": "Microservice for multilingual support in SkillForge AI platform",
        "database": "skillforge_localization", 
        "specific_deps": ["babel", "googletrans"],
        "endpoints": ["translations", "languages", "locales"]
    },
    {
        "name": "realtime-collaboration-service",
        "port": 8011,
        "description": "Microservice for real-time collaboration in SkillForge AI platform",
        "database": "skillforge_collaboration",
        "specific_deps": ["websockets", "socketio"],
        "endpoints": ["rooms", "collaboration", "presence"]
    },
    {
        "name": "company-service",
        "port": 8012,
        "description": "Microservice for company management in SkillForge AI platform",
        "database": "skillforge_companies",
        "specific_deps": [],
        "endpoints": ["companies", "departments", "roles"]
    },
    {
        "name": "subscription-service",
        "port": 8013,
        "description": "Microservice for subscription management in SkillForge AI platform",
        "database": "skillforge_subscriptions",
        "specific_deps": [],
        "endpoints": ["subscriptions", "plans", "billing"]
    },
    {
        "name": "payment-service",
        "port": 8014,
        "description": "Microservice for payment processing in SkillForge AI platform",
        "database": "skillforge_payments",
        "specific_deps": ["stripe"],
        "endpoints": ["payments", "transactions", "refunds"]
    },
    {
        "name": "notification-service",
        "port": 8015,
        "description": "Microservice for notifications (push/email) in SkillForge AI platform",
        "database": "skillforge_notifications",
        "specific_deps": ["fcm-django", "sendgrid"],
        "endpoints": ["notifications", "templates", "delivery"]
    },
    {
        "name": "analytics-service",
        "port": 8016,
        "description": "Microservice for analytics and metrics in SkillForge AI platform",
        "database": "skillforge_analytics",
        "specific_deps": ["pandas", "numpy"],
        "endpoints": ["analytics", "metrics", "reports"]
    },
    {
        "name": "content-service",
        "port": 8017,
        "description": "Microservice for content management in SkillForge AI platform",
        "database": "skillforge_content",
        "specific_deps": ["markdown"],
        "endpoints": ["content", "media", "documents"]
    },
    {
        "name": "search-service", 
        "port": 8018,
        "description": "Microservice for search and indexation in SkillForge AI platform",
        "database": "skillforge_search",
        "specific_deps": ["elasticsearch"],
        "endpoints": ["search", "indexing", "filters"]
    },
    {
        "name": "storage-service",
        "port": 8019,
        "description": "Microservice for file storage management in SkillForge AI platform",
        "database": "skillforge_storage",
        "specific_deps": ["boto3", "google-cloud-storage"],
        "endpoints": ["files", "uploads", "downloads"]
    },
    {
        "name": "workflow-service",
        "port": 8020,
        "description": "Microservice for workflow orchestration in SkillForge AI platform",
        "database": "skillforge_workflows",
        "specific_deps": ["celery"],
        "endpoints": ["workflows", "steps", "execution"]
    },
    {
        "name": "audit-service",
        "port": 8021,
        "description": "Microservice for logs and audit trail in SkillForge AI platform",
        "database": "skillforge_audit",
        "specific_deps": [],
        "endpoints": ["audits", "logs", "trails"]
    },
    {
        "name": "integration-service",
        "port": 8022,
        "description": "Microservice for external integrations in SkillForge AI platform", 
        "database": "skillforge_integrations",
        "specific_deps": ["requests-oauthlib"],
        "endpoints": ["integrations", "webhooks", "apis"]
    }
]

def create_service_directories(service_name):
    """Create the directory structure for a service."""
    base_path = os.path.join(BACKEND_DIR, service_name)
    
    directories = [
        "app",
        "app/api",
        "app/api/v1", 
        "app/api/v1/endpoints",
        "app/core",
        "app/models",
        "app/schemas", 
        "app/crud"
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_path, directory)
        os.makedirs(dir_path, exist_ok=True)
        
        # Create __init__.py files
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")

def create_main_py(service):
    """Create main.py file for a service."""
    service_name = service["name"]
    port = service["port"]
    description = service["description"]
    
    content = f'''"""
SkillForge AI - {service_name.replace("-", " ").title()}
FastAPI application entry point
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
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting SkillForge AI {service_name.replace("-", " ").title()}...")
    
    # Initialize database
    await create_db_and_tables()
    logger.info("Database tables created/verified")
    
    # Initialize cache (Redis)
    cache_connected = await initialize_cache()
    if cache_connected:
        logger.info("Redis cache initialized successfully")
    else:
        logger.warning("Redis cache not available - running without cache")
    
    logger.info("Service-specific components initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillForge AI {service_name.replace("-", " ").title()}...")
    await shutdown_cache()
    logger.info("Services shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="SkillForge AI - {service_name.replace("-", " ").title()}",
    description="{description}",
    version="1.0.0",
    openapi_url=f"{{settings.API_V1_STR}}/openapi.json",
    docs_url=f"{{settings.API_V1_STR}}/docs",
    redoc_url=f"{{settings.API_V1_STR}}/redoc",
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

# Add Prometheus monitoring middleware
if settings.ENABLE_METRICS:
    app.add_middleware(PrometheusMiddleware)

# Add rate limiting
app.state.limiter = limiter
app.state.environment = settings.ENVIRONMENT
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
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {{
        "service": "skillforge-{service_name}",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "description": "{description.split(' in SkillForge AI platform')[0]}"
    }}


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    # Check database connection
    db_healthy = await check_db_connection()
    
    # Check cache connection
    cache_status = "healthy" if cache_service.is_connected else "unavailable"
    
    # Overall status
    status = "healthy" if db_healthy else "unhealthy"
    
    return {{
        "status": status,
        "timestamp": time.time(),
        "service": "{service_name}",
        "version": "1.0.0",
        "checks": {{
            "database": "healthy" if db_healthy else "unhealthy",
            "cache": cache_status,
            "metrics": "enabled" if settings.ENABLE_METRICS else "disabled"
        }}
    }}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.ENABLE_METRICS:
        return JSONResponse(
            status_code=404,
            content={{"error": "Metrics disabled"}}
        )
    
    # Collect latest metrics
    await MetricsCollector.collect_all()
    
    # Return metrics in Prometheus format
    return PlainTextResponse(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {{str(exc)}}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={{"message": "Internal server error", "detail": str(exc)}}
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={port},
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )'''

    file_path = os.path.join(BACKEND_DIR, service_name, "app", "main.py")
    with open(file_path, "w") as f:
        f.write(content)

def create_dockerfile(service):
    """Create Dockerfile for a service."""
    service_name = service["name"]
    port = service["port"]
    
    content = f'''# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PYTHONPATH="/app" \\
    PORT={port}

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r skillforge && useradd -r -g skillforge skillforge

# Install Python dependencies
COPY apps/backend/{service_name}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY apps/backend/{service_name}/ .

# Change ownership of the app directory to the skillforge user
RUN chown -R skillforge:skillforge /app

# Switch to non-root user
USER skillforge

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:{port}/health')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]'''

    file_path = os.path.join(BACKEND_DIR, service_name, "Dockerfile")
    with open(file_path, "w") as f:
        f.write(content)

def create_requirements_txt(service):
    """Create requirements.txt file for a service."""
    service_name = service["name"]
    specific_deps = service.get("specific_deps", [])
    
    base_requirements = [
        "# FastAPI and ASGI",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "",
        "# Database", 
        "sqlmodel==0.0.14",
        "asyncpg==0.29.0",
        "psycopg2-binary",
        "alembic==1.13.1",
        "",
        "# Authentication & Security",
        "python-jose[cryptography]==3.3.0",
        "PyJWT==2.8.0",
        "cryptography==46.0.1",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "",
        "# HTTP Requests",
        "httpx==0.25.2",
        "requests==2.31.0",
        "",
        "# Environment & Configuration",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "",
        "# Email",
        "emails==0.6.0",
        "jinja2==3.1.2",
        "",
        "# Validation & Serialization", 
        "email-validator==2.1.0",
        "pydantic[email]==2.5.2",
        "",
        "# Date & Time",
        "python-dateutil==2.8.2",
        "",
        "# Utilities",
        "tenacity==8.2.3",
        "celery==5.3.4",
        "redis==5.0.1",
        "slowapi==0.1.9",
        "",
        "# Monitoring & Logging",
        "prometheus-client==0.19.0",
        "structlog==23.2.0",
        "",
        "# Development Dependencies",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "pytest-cov==4.1.0",
        "faker==20.1.0",
        "aiosqlite==0.19.0",
        ""
    ]
    
    if specific_deps:
        base_requirements.extend([
            "# Service-specific dependencies"
        ])
        for dep in specific_deps:
            base_requirements.append(dep)
    
    content = "\\n".join(base_requirements)
    
    file_path = os.path.join(BACKEND_DIR, service_name, "requirements.txt")
    with open(file_path, "w") as f:
        f.write(content)

def create_env_example(service):
    """Create .env.example file for a service."""
    service_name = service["name"]
    port = service["port"]
    database = service["database"]
    
    content = f'''# Environment Configuration
ENVIRONMENT=development
DEBUG=True

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME="SkillForge AI {service_name.replace("-", " ").title()}"

# Database Configuration
# IMPORTANT: Never commit real credentials to git!
DATABASE_URL=postgresql+asyncpg://your_user:your_secure_password@localhost:5432/{database}
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=GENERATE_A_SECURE_PASSWORD_HERE
POSTGRES_DB={database}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security & Authentication
# IMPORTANT: Generate a secure secret key with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=GENERATE_A_SECURE_SECRET_KEY_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","https://your-domain.com"]
ALLOWED_HOSTS=["localhost","127.0.0.1","your-domain.com"]

# Redis Configuration (for caching and sessions)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Email Configuration
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=YOUR_EMAIL_APP_PASSWORD_HERE
EMAILS_FROM_EMAIL=noreply@your-domain.com
EMAILS_FROM_NAME="SkillForge AI"

# Service Configuration
SERVICE_PORT={port}
SERVICE_NAME={service_name}

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# External Services
USER_SERVICE_URL=http://user-service:8000

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090

# Testing
TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/{database}_test'''

    file_path = os.path.join(BACKEND_DIR, service_name, ".env.example")
    with open(file_path, "w") as f:
        f.write(content)

def main():
    """Create all microservices."""
    print("Creating 22 SkillForge AI backend microservices...")
    
    for i, service in enumerate(SERVICES, 1):
        service_name = service["name"]
        print(f"\\n[{i}/22] Creating {service_name}...")
        
        # Create directory structure
        create_service_directories(service_name)
        
        # Create main files
        create_main_py(service)
        create_dockerfile(service)
        create_requirements_txt(service) 
        create_env_example(service)
        
        print(f"✓ {service_name} created successfully")
    
    print("\\n🎉 All 22 microservices created successfully!")
    print("\\nNext steps:")
    print("1. Review each service configuration")
    print("2. Customize endpoints and models for each service")
    print("3. Set up proper database schemas")
    print("4. Configure CI/CD pipelines")

if __name__ == "__main__":
    main()