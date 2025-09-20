"""
Monitoring and metrics for SkillForge AI User Service using Prometheus
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import asynccontextmanager

from prometheus_client import (
    Counter, Histogram, Gauge, Info, 
    CollectorRegistry, generate_latest,
    CONTENT_TYPE_LATEST
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create custom registry for our metrics
registry = CollectorRegistry()

# Application info metric
app_info = Info(
    'skillforge_app_info', 
    'Application information',
    registry=registry
)

# HTTP request metrics
http_requests_total = Counter(
    'skillforge_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'skillforge_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

http_requests_in_progress = Gauge(
    'skillforge_http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint'],
    registry=registry
)

# Authentication metrics
auth_attempts_total = Counter(
    'skillforge_auth_attempts_total',
    'Total authentication attempts',
    ['type', 'status'],  # type: login/register/reset, status: success/failure
    registry=registry
)

auth_sessions_active = Gauge(
    'skillforge_auth_sessions_active',
    'Number of active user sessions',
    registry=registry
)

# Database metrics
db_connections_active = Gauge(
    'skillforge_db_connections_active',
    'Active database connections',
    registry=registry
)

db_operations_total = Counter(
    'skillforge_db_operations_total',
    'Total database operations',
    ['operation', 'table', 'status'],
    registry=registry
)

db_operation_duration_seconds = Histogram(
    'skillforge_db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table'],
    registry=registry
)

# Business metrics
users_total = Gauge(
    'skillforge_users_total',
    'Total number of users',
    ['role', 'status'],
    registry=registry
)

companies_total = Gauge(
    'skillforge_companies_total', 
    'Total number of companies',
    ['size', 'status'],
    registry=registry
)

user_registrations_total = Counter(
    'skillforge_user_registrations_total',
    'Total user registrations',
    ['role'],
    registry=registry
)

# Email metrics
emails_sent_total = Counter(
    'skillforge_emails_sent_total',
    'Total emails sent',
    ['type', 'status'],  # type: verification/reset/welcome, status: success/failure
    registry=registry
)

# Rate limiting metrics
rate_limit_hits_total = Counter(
    'skillforge_rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint', 'user_type'],
    registry=registry
)

# Error metrics
errors_total = Counter(
    'skillforge_errors_total',
    'Total application errors',
    ['error_type', 'endpoint'],
    registry=registry
)

# Cache metrics (Redis)
cache_operations_total = Counter(
    'skillforge_cache_operations_total',
    'Total cache operations',
    ['operation', 'status'],  # operation: get/set/delete, status: hit/miss/error
    registry=registry
)

cache_hit_ratio = Gauge(
    'skillforge_cache_hit_ratio',
    'Cache hit ratio (0-1)',
    registry=registry
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics automatically."""
    
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        
        # Normalize path for metrics (remove IDs, etc.)
        endpoint = self._normalize_path(path)
        
        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Record successful request
            http_requests_total.labels(
                method=method, 
                endpoint=endpoint, 
                status_code=status_code
            ).inc()
            
            return response
            
        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=method, 
                endpoint=endpoint, 
                status_code=500
            ).inc()
            
            errors_total.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            
            raise
            
        finally:
            # Record duration and decrement in-progress
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method, 
                endpoint=endpoint
            ).observe(duration)
            
            http_requests_in_progress.labels(
                method=method, 
                endpoint=endpoint
            ).dec()
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics to avoid high cardinality."""
        # Replace UUIDs and IDs with placeholders
        import re
        
        # Replace UUIDs
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{uuid}',
            path,
            flags=re.IGNORECASE
        )
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Keep only first 3 path segments to avoid explosion
        segments = path.strip('/').split('/')[:3]
        normalized = '/' + '/'.join(segments)
        
        return normalized


def record_auth_attempt(auth_type: str, success: bool):
    """Record authentication attempt."""
    status = "success" if success else "failure"
    auth_attempts_total.labels(type=auth_type, status=status).inc()


def record_user_registration(role: str):
    """Record new user registration."""
    user_registrations_total.labels(role=role).inc()


def record_email_sent(email_type: str, success: bool):
    """Record email sending attempt."""
    status = "success" if success else "failure"
    emails_sent_total.labels(type=email_type, status=status).inc()


def record_rate_limit_hit(endpoint: str, user_type: str):
    """Record rate limit hit."""
    rate_limit_hits_total.labels(endpoint=endpoint, user_type=user_type).inc()


def record_error(error_type: str, endpoint: str):
    """Record application error."""
    errors_total.labels(error_type=error_type, endpoint=endpoint).inc()


@asynccontextmanager
async def track_db_operation(operation: str, table: str):
    """Context manager to track database operations."""
    start_time = time.time()
    
    try:
        yield
        # Record successful operation
        db_operations_total.labels(
            operation=operation, 
            table=table, 
            status="success"
        ).inc()
        
    except Exception as e:
        # Record failed operation
        db_operations_total.labels(
            operation=operation, 
            table=table, 
            status="error"
        ).inc()
        raise
        
    finally:
        # Record duration
        duration = time.time() - start_time
        db_operation_duration_seconds.labels(
            operation=operation, 
            table=table
        ).observe(duration)


def db_operation_tracker(operation: str, table: str):
    """Decorator to track database operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with track_db_operation(operation, table):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def update_business_metrics():
    """Update business metrics (called periodically)."""
    try:
        from app.core.database import get_session
        from app.models import User, CompanyProfile
        from sqlalchemy import func, select
        
        async with get_session() as session:
            # Count users by role and status
            user_counts = await session.execute(
                select(User.role, User.status, func.count(User.id))
                .group_by(User.role, User.status)
            )
            
            for role, status, count in user_counts:
                users_total.labels(role=role.value, status=status.value).set(count)
            
            # Count companies by size and status  
            company_counts = await session.execute(
                select(CompanyProfile.size, func.count(CompanyProfile.id))
                .where(CompanyProfile.is_active == True)
                .group_by(CompanyProfile.size)
            )
            
            for size, count in company_counts:
                companies_total.labels(size=size.value, status="active").set(count)
                
    except Exception as e:
        logger.error(f"Failed to update business metrics: {str(e)}")


async def update_db_metrics():
    """Update database connection metrics."""
    try:
        from app.core.database import get_engine
        
        engine = get_engine()
        pool = engine.pool
        
        # Database connection metrics
        db_connections_active.set(pool.checkedout())
        
    except Exception as e:
        logger.error(f"Failed to update database metrics: {str(e)}")


async def update_cache_metrics():
    """Update cache metrics."""
    try:
        from app.core.rate_limiting import redis_client
        
        if redis_client:
            # Redis is available, update cache metrics
            info = await redis_client.info()
            
            # Calculate hit ratio if available
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            if total > 0:
                hit_ratio = hits / total
                cache_hit_ratio.set(hit_ratio)
                
    except Exception as e:
        logger.error(f"Failed to update cache metrics: {str(e)}")


def get_metrics() -> str:
    """Get Prometheus metrics in text format."""
    return generate_latest(registry).decode('utf-8')


def get_metrics_content_type() -> str:
    """Get content type for metrics endpoint."""
    return CONTENT_TYPE_LATEST


def initialize_app_info():
    """Initialize application info metric."""
    app_info.info({
        'version': settings.VERSION if hasattr(settings, 'VERSION') else '1.0.0',
        'environment': settings.ENVIRONMENT,
        'service': 'user-service'
    })


# Initialize app info on module load
initialize_app_info()


class MetricsCollector:
    """Collector class for organizing metrics updates."""
    
    @staticmethod
    async def collect_all():
        """Collect all metrics."""
        await update_business_metrics()
        await update_db_metrics()
        await update_cache_metrics()
    
    @staticmethod
    async def health_check() -> Dict[str, Any]:
        """Health check that includes metrics status."""
        try:
            await MetricsCollector.collect_all()
            return {
                "status": "healthy",
                "metrics": "available",
                "registry_collectors": len(registry._collector_to_names)
            }
        except Exception as e:
            return {
                "status": "degraded", 
                "error": str(e),
                "metrics": "partial"
            }