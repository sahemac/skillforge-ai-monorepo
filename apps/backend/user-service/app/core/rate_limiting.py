"""
Rate limiting configuration for SkillForge AI User Service
"""

import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Optional
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RateLimitConfig:
    """Rate limit configuration for different endpoints."""
    
    # Authentication endpoints (stricter limits)
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute" 
    AUTH_PASSWORD_RESET = "3/hour"
    AUTH_VERIFY_EMAIL = "10/hour"
    
    # API endpoints (normal limits)
    API_READ = "100/minute"
    API_WRITE = "30/minute"
    API_UPLOAD = "10/minute"
    
    # Admin endpoints (higher limits)
    ADMIN_READ = "200/minute"
    ADMIN_WRITE = "50/minute"
    
    # Public endpoints (moderate limits)
    PUBLIC_READ = "50/minute"
    PUBLIC_SEARCH = "20/minute"


def get_redis_connection() -> Optional[redis.Redis]:
    """Get Redis connection for rate limiting."""
    try:
        if not all([settings.REDIS_HOST, settings.REDIS_PORT]):
            logger.warning("Redis not configured, using in-memory rate limiting")
            return None
            
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB or 0,
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        return redis_client
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        return None


def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from request for user-specific rate limiting."""
    try:
        # Try to get user from JWT token
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Try to get from headers
        user_id = request.headers.get('X-User-ID')
        if user_id:
            return f"user:{user_id}"
            
        # Fall back to IP address
        return get_remote_address(request)
        
    except Exception:
        return get_remote_address(request)


# Initialize limiter with Redis or in-memory storage
redis_client = get_redis_connection()

if redis_client:
    limiter = Limiter(
        key_func=get_user_id_from_request,
        storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB or 0}"
    )
    logger.info("Rate limiting initialized with Redis backend")
else:
    limiter = Limiter(
        key_func=get_user_id_from_request
    )
    logger.info("Rate limiting initialized with in-memory backend")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler."""
    logger.warning(
        f"Rate limit exceeded for {get_user_id_from_request(request)} "
        f"on {request.url.path}"
    )
    
    response_data = {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": exc.retry_after,
        "limit": exc.detail
    }
    
    return HTTPException(
        status_code=429,
        detail=response_data,
        headers={"Retry-After": str(exc.retry_after)}
    )


# Rate limiting decorators for different endpoint types
def auth_rate_limit(rate: str = RateLimitConfig.AUTH_LOGIN):
    """Rate limiter for authentication endpoints."""
    return limiter.limit(rate)


def api_rate_limit(rate: str = RateLimitConfig.API_READ):
    """Rate limiter for API endpoints.""" 
    return limiter.limit(rate)


def upload_rate_limit(rate: str = RateLimitConfig.API_UPLOAD):
    """Rate limiter for upload endpoints."""
    return limiter.limit(rate)


def admin_rate_limit(rate: str = RateLimitConfig.ADMIN_READ):
    """Rate limiter for admin endpoints."""
    return limiter.limit(rate)


def public_rate_limit(rate: str = RateLimitConfig.PUBLIC_READ):
    """Rate limiter for public endpoints."""
    return limiter.limit(rate)


async def check_redis_health() -> bool:
    """Check Redis connection health."""
    if not redis_client:
        return False
        
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False


async def get_rate_limit_stats(user_key: str) -> dict:
    """Get rate limit statistics for a user."""
    if not redis_client:
        return {"backend": "in-memory", "stats": "unavailable"}
    
    try:
        # Get current usage for different rate limits
        stats = {}
        
        # Check different time windows
        for window in ["minute", "hour", "day"]:
            key = f"rate_limit:{user_key}:{window}"
            current = await redis_client.get(key)
            ttl = await redis_client.ttl(key)
            
            stats[window] = {
                "current": int(current) if current else 0,
                "reset_in": ttl if ttl > 0 else 0
            }
        
        return {
            "backend": "redis",
            "user_key": user_key,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get rate limit stats: {str(e)}")
        return {"backend": "redis", "error": str(e)}


async def reset_user_rate_limits(user_key: str) -> bool:
    """Reset rate limits for a specific user (admin function)."""
    if not redis_client:
        return False
        
    try:
        # Find all rate limit keys for this user
        pattern = f"rate_limit:{user_key}:*"
        keys = await redis_client.keys(pattern)
        
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Reset rate limits for user: {user_key}")
            return True
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset rate limits for {user_key}: {str(e)}")
        return False