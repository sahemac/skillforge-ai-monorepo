"""
Structured logging configuration for SkillForge AI Company Service
Uses JSON formatting with correlation IDs for request tracing
"""

import logging
import uuid
import time
from typing import Dict, Any, Optional
from contextvars import ContextVar
from functools import wraps

import structlog
from pythonjsonlogger import jsonlogger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

# Context variables for correlation tracking
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

settings = get_settings()


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to all requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = (
            request.headers.get('x-correlation-id') or 
            request.headers.get('x-request-id') or
            str(uuid.uuid4())
        )
        
        # Set correlation ID in context
        correlation_id_var.set(correlation_id)
        
        # Extract user ID from IAP headers if available
        user_id = request.headers.get('x-goog-iap-jwt-assertion-sub', '')
        user_id_var.set(user_id)
        
        # Add correlation ID to response headers
        response = await call_next(request)
        response.headers['x-correlation-id'] = correlation_id
        
        return response


def get_correlation_id() -> str:
    """Get current correlation ID from context."""
    return correlation_id_var.get('')


def get_user_id() -> str:
    """Get current user ID from context."""
    return user_id_var.get('')


class CorrelationFilter(logging.Filter):
    """Add correlation ID and user ID to log records."""
    
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        record.user_id = get_user_id()
        return True


class JsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = time.time()
        log_record['service'] = 'company-service'
        log_record['environment'] = settings.ENVIRONMENT
        log_record['version'] = getattr(settings, 'VERSION', '1.0.0')
        
        # Add correlation ID and user ID
        log_record['correlation_id'] = getattr(record, 'correlation_id', '')
        log_record['user_id'] = getattr(record, 'user_id', '')
        
        # Add request context if available
        if hasattr(record, 'request_method'):
            log_record['request'] = {
                'method': getattr(record, 'request_method', ''),
                'path': getattr(record, 'request_path', ''),
                'query': getattr(record, 'request_query', ''),
                'user_agent': getattr(record, 'request_user_agent', ''),
                'ip': getattr(record, 'request_ip', '')
            }
        
        # Add response context if available
        if hasattr(record, 'response_status'):
            log_record['response'] = {
                'status_code': getattr(record, 'response_status', 0),
                'duration_ms': getattr(record, 'response_duration_ms', 0)
            }


def configure_logging():
    """Configure structured logging for the application."""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.ENVIRONMENT == 'production' else logging.DEBUG)
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create JSON formatter
    json_formatter = JsonFormatter(
        fmt='%(timestamp)s %(name)s %(levelname)s %(message)s'
    )
    
    # Create and configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(json_formatter)
    handler.addFilter(CorrelationFilter())
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Configure specific loggers
    configure_logger('uvicorn.access', logging.INFO)
    configure_logger('uvicorn.error', logging.INFO)
    configure_logger('sqlalchemy.engine', logging.WARNING)
    configure_logger('app', logging.DEBUG if settings.ENVIRONMENT != 'production' else logging.INFO)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_logger(name: str, level: int):
    """Configure a specific logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = True


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request_start(request: Request) -> Dict[str, Any]:
    """Log request start with context."""
    logger = get_logger('app.requests')
    
    context = {
        'event': 'request_start',
        'method': request.method,
        'path': request.url.path,
        'query': str(request.url.query) if request.url.query else '',
        'user_agent': request.headers.get('user-agent', ''),
        'ip': getattr(request.client, 'host', '') if request.client else '',
        'correlation_id': get_correlation_id(),
        'user_id': get_user_id()
    }
    
    logger.info("Request started", **context)
    return context


def log_request_end(context: Dict[str, Any], response: Response, duration_ms: float):
    """Log request end with context."""
    logger = get_logger('app.requests')
    
    context.update({
        'event': 'request_end',
        'status_code': response.status_code,
        'duration_ms': round(duration_ms, 2)
    })
    
    # Determine log level based on status code
    if response.status_code >= 500:
        logger.error("Request completed with server error", **context)
    elif response.status_code >= 400:
        logger.warning("Request completed with client error", **context)
    else:
        logger.info("Request completed successfully", **context)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request start
        context = log_request_start(request)
        
        try:
            response = await call_next(request)
            
            # Log request end
            duration_ms = (time.time() - start_time) * 1000
            log_request_end(context, response, duration_ms)
            
            return response
            
        except Exception as e:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000
            logger = get_logger('app.requests')
            logger.error(
                "Request failed with exception",
                **context,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )
            raise


def log_company_operation(operation: str, company_id: Optional[str] = None, success: bool = True, error: Optional[str] = None):
    """Log company-specific operations."""
    logger = get_logger('app.company')
    
    context = {
        'operation': operation,
        'company_id': company_id,
        'success': success,
        'correlation_id': get_correlation_id(),
        'user_id': get_user_id()
    }
    
    if error:
        context['error'] = error
        logger.error("Company operation failed", **context)
    else:
        logger.info("Company operation completed", **context)


def log_business_event(event_type: str, entity_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    """Log business events."""
    logger = get_logger('app.business')
    
    context = {
        'event_type': event_type,
        'entity_id': entity_id,
        'correlation_id': get_correlation_id(),
        'user_id': get_user_id()
    }
    
    if metadata:
        context.update(metadata)
    
    logger.info("Business event occurred", **context)


def structured_log_decorator(operation: str):
    """Decorator to add structured logging to functions."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger('app.operations')
            start_time = time.time()
            
            logger.info(
                f"Starting {operation}",
                operation=operation,
                correlation_id=get_correlation_id(),
                user_id=get_user_id()
            )
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Completed {operation}",
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=get_correlation_id(),
                    user_id=get_user_id()
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Failed {operation}",
                    operation=operation,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=get_correlation_id(),
                    user_id=get_user_id()
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger('app.operations')
            start_time = time.time()
            
            logger.info(
                f"Starting {operation}",
                operation=operation,
                correlation_id=get_correlation_id(),
                user_id=get_user_id()
            )
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Completed {operation}",
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=get_correlation_id(),
                    user_id=get_user_id()
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Failed {operation}",
                    operation=operation,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=round(duration_ms, 2),
                    correlation_id=get_correlation_id(),
                    user_id=get_user_id()
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator