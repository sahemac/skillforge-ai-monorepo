"""
Redis cache service for SkillForge AI User Service
"""

import json
import logging
from typing import Any, Optional, Union, List, Dict
from datetime import timedelta
import pickle
import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheService:
    """Redis cache service for caching data."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=False,  # We'll handle encoding ourselves
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            logger.info("Successfully connected to Redis")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Disconnected from Redis")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected and self.redis_client is not None
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage."""
        try:
            # Try JSON first for simple types
            if isinstance(data, (str, int, float, bool, list, dict, type(None))):
                return json.dumps(data).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(data)
        except Exception:
            # Fallback to pickle
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to pickle
            return pickle.loads(data)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set a value in cache."""
        if not self.is_connected:
            logger.debug("Cache not connected, skipping set operation")
            return False
        
        try:
            serialized_value = self._serialize(value)
            
            if ttl is None:
                ttl = settings.CACHE_TTL
            elif isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.is_connected:
            logger.debug("Cache not connected, skipping get operation")
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {str(e)}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        if not self.is_connected:
            return -1
        
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {str(e)}")
            return -1
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration for a key."""
        if not self.is_connected:
            return False
        
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            result = await self.redis_client.expire(key, ttl)
            return result
            
        except Exception as e:
            logger.error(f"Failed to set expiration for key {key}: {str(e)}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self.is_connected:
            return []
        
        try:
            keys = await self.redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
            
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {str(e)}")
            return []
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.is_connected:
            return 0
        
        try:
            keys = await self.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                return result
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear keys with pattern {pattern}: {str(e)}")
            return 0
    
    async def flush_all(self) -> bool:
        """Clear all cache."""
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.flushdb()
            logger.info("Cache flushed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to flush cache: {str(e)}")
            return False
    
    async def info(self) -> Dict[str, Any]:
        """Get Redis info."""
        if not self.is_connected:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses")
            }
            
        except Exception as e:
            logger.error(f"Failed to get Redis info: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global cache service instance
cache_service = CacheService()


# Convenience functions
async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    return await cache_service.get(key)


async def set_cache(
    key: str, 
    value: Any, 
    ttl: Optional[Union[int, timedelta]] = None
) -> bool:
    """Set value in cache."""
    return await cache_service.set(key, value, ttl)


async def delete_cache(key: str) -> bool:
    """Delete key from cache."""
    return await cache_service.delete(key)


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    return await cache_service.exists(key)


# Cache key generators
class CacheKeys:
    """Cache key generators for different types of data."""
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def user_session(session_token: str) -> str:
        return f"user:session:{session_token}"
    
    @staticmethod
    def user_permissions(user_id: str) -> str:
        return f"user:permissions:{user_id}"
    
    @staticmethod
    def company_profile(company_id: str) -> str:
        return f"company:profile:{company_id}"
    
    @staticmethod
    def company_members(company_id: str) -> str:
        return f"company:members:{company_id}"
    
    @staticmethod
    def public_users(page: int = 1, limit: int = 20) -> str:
        return f"public:users:{page}:{limit}"
    
    @staticmethod
    def public_companies(page: int = 1, limit: int = 20) -> str:
        return f"public:companies:{page}:{limit}"
    
    @staticmethod
    def verification_token(token: str) -> str:
        return f"auth:verification:{token}"
    
    @staticmethod
    def password_reset_token(token: str) -> str:
        return f"auth:reset:{token}"
    
    @staticmethod
    def rate_limit(user_id: str, endpoint: str) -> str:
        return f"rate_limit:{user_id}:{endpoint}"


# Cache decorators
def cache_result(
    key_func: callable,
    ttl: Optional[Union[int, timedelta]] = None
):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_func(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user."""
    patterns = [
        f"user:profile:{user_id}",
        f"user:permissions:{user_id}",
        f"user:session:*",  # Sessions might not have direct user_id
        f"public:users:*",  # Public listings might include this user
    ]
    
    for pattern in patterns:
        await cache_service.clear_pattern(pattern)


async def invalidate_company_cache(company_id: str):
    """Invalidate all cache entries for a company."""
    patterns = [
        f"company:profile:{company_id}",
        f"company:members:{company_id}",
        f"public:companies:*",  # Public listings might include this company
    ]
    
    for pattern in patterns:
        await cache_service.clear_pattern(pattern)


async def initialize_cache() -> bool:
    """Initialize cache service."""
    return await cache_service.connect()


async def shutdown_cache():
    """Shutdown cache service."""
    await cache_service.disconnect()