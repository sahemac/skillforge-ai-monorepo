"""
Monitoring and metrics for SkillForge AI Company Service using Prometheus
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
    'skillforge_company_app_info', 
    'Company Service application information',
    registry=registry
)

# HTTP request metrics
http_requests_total = Counter(
    'skillforge_company_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'skillforge_company_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

http_requests_in_progress = Gauge(
    'skillforge_company_http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint'],
    registry=registry
)

# Company-specific business metrics
companies_total = Gauge(
    'skillforge_companies_total', 
    'Total number of companies',
    ['size', 'industry', 'status'],
    registry=registry
)

company_registrations_total = Counter(
    'skillforge_company_registrations_total',
    'Total company registrations',
    ['size', 'industry'],
    registry=registry
)

company_profiles_updates_total = Counter(
    'skillforge_company_profile_updates_total',
    'Total company profile updates',
    ['field_updated'],
    registry=registry
)

company_employees_total = Gauge(
    'skillforge_company_employees_total',
    'Total employees across all companies',
    ['company_size'],
    registry=registry
)

# API Gateway integration metrics
api_gateway_requests_total = Counter(
    'skillforge_company_api_gateway_requests_total',
    'Total requests through API Gateway',
    ['gateway_endpoint', 'status_code'],
    registry=registry
)

api_gateway_response_time = Histogram(
    'skillforge_company_api_gateway_response_time_seconds',
    'API Gateway response time',
    ['gateway_endpoint'],
    registry=registry
)

# Error metrics
errors_total = Counter(
    'skillforge_company_errors_total',
    'Total application errors',
    ['error_type', 'endpoint'],
    registry=registry
)

# Cache metrics (if Redis is used)
cache_operations_total = Counter(
    'skillforge_company_cache_operations_total',
    'Total cache operations',
    ['operation', 'status'],
    registry=registry
)

# Database metrics (if database is used)
db_operations_total = Counter(
    'skillforge_company_db_operations_total',
    'Total database operations',
    ['operation', 'table', 'status'],
    registry=registry
)

db_operation_duration_seconds = Histogram(
    'skillforge_company_db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table'],
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
            
            # Record API Gateway metrics if this is a gateway request
            if 'x-forwarded-for' in request.headers or 'x-gateway' in request.headers:
                api_gateway_requests_total.labels(
                    gateway_endpoint=endpoint,
                    status_code=status_code
                ).inc()
                
                duration = time.time() - start_time
                api_gateway_response_time.labels(
                    gateway_endpoint=endpoint
                ).observe(duration)
            
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
        import re
        
        # Replace UUIDs and IDs with placeholders
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


def record_company_registration(size: str, industry: str):
    """Record new company registration."""
    company_registrations_total.labels(size=size, industry=industry).inc()


def record_company_profile_update(field: str):
    """Record company profile update."""
    company_profiles_updates_total.labels(field_updated=field).inc()


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
        # Mock implementation - replace with actual database queries
        # In real implementation, query company database for metrics
        
        # Example: Count companies by size and industry
        # This would be replaced with actual database queries
        companies_total.labels(size="small", industry="tech", status="active").set(50)
        companies_total.labels(size="medium", industry="tech", status="active").set(25)
        companies_total.labels(size="large", industry="tech", status="active").set(10)
        
        # Example: Count total employees
        company_employees_total.labels(company_size="small").set(500)
        company_employees_total.labels(company_size="medium").set(750)
        company_employees_total.labels(company_size="large").set(2000)
        
    except Exception as e:
        logger.error(f"Failed to update business metrics: {str(e)}")


async def update_cache_metrics():
    """Update cache metrics."""
    try:
        # Mock implementation - replace with actual Redis client
        # Record cache operations if Redis is available
        cache_operations_total.labels(operation="get", status="hit").inc(0)
        cache_operations_total.labels(operation="get", status="miss").inc(0)
        cache_operations_total.labels(operation="set", status="success").inc(0)
        
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
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': settings.ENVIRONMENT,
        'service': 'company-service'
    })


# Initialize app info on module load
initialize_app_info()


class MetricsCollector:
    """Collector class for organizing metrics updates."""
    
    @staticmethod
    async def collect_all():
        """Collect all metrics."""
        await update_business_metrics()
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