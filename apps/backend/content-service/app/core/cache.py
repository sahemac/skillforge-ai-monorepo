"""
Redis cache utilities for Content Service
"""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from ..core.config import get_settings

settings = get_settings()

# Global Redis connection
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis connection instance."""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


class CacheManager:
    """Cache manager for content service operations."""

    def __init__(self):
        self.redis_client = None

    async def _get_client(self):
        """Get Redis client."""
        if not self.redis_client:
            self.redis_client = await get_redis()
        return self.redis_client

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None,
        serialize: bool = True
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds or timedelta
            serialize: Whether to serialize the value as JSON

        Returns:
            True if successful
        """
        try:
            client = await self._get_client()

            if serialize:
                if isinstance(value, (dict, list, tuple)):
                    cached_value = json.dumps(value, default=str)
                else:
                    cached_value = str(value)
            else:
                cached_value = value

            if expire:
                if isinstance(expire, timedelta):
                    expire_seconds = int(expire.total_seconds())
                else:
                    expire_seconds = expire

                await client.setex(key, expire_seconds, cached_value)
            else:
                await client.set(key, cached_value)

            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def get(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            deserialize: Whether to deserialize JSON value
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            client = await self._get_client()
            value = await client.get(key)

            if value is None:
                return default

            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value

            return value

        except Exception as e:
            print(f"Cache get error: {e}")
            return default

    async def delete(self, *keys: str) -> int:
        """
        Delete keys from cache.

        Args:
            keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            if not keys:
                return 0

            client = await self._get_client()
            return await client.delete(*keys)

        except Exception as e:
            print(f"Cache delete error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            client = await self._get_client()
            return bool(await client.exists(key))

        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def expire(self, key: str, seconds: Union[int, timedelta]) -> bool:
        """
        Set expiration time for key.

        Args:
            key: Cache key
            seconds: Expiration time in seconds or timedelta

        Returns:
            True if successful
        """
        try:
            client = await self._get_client()

            if isinstance(seconds, timedelta):
                expire_seconds = int(seconds.total_seconds())
            else:
                expire_seconds = seconds

            return bool(await client.expire(key, expire_seconds))

        except Exception as e:
            print(f"Cache expire error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get time to live for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            client = await self._get_client()
            return await client.ttl(key)

        except Exception as e:
            print(f"Cache TTL error: {e}")
            return -2

    async def keys(self, pattern: str = "*") -> list:
        """
        Get keys matching pattern.

        Args:
            pattern: Pattern to match (supports wildcards)

        Returns:
            List of matching keys
        """
        try:
            client = await self._get_client()
            return await client.keys(pattern)

        except Exception as e:
            print(f"Cache keys error: {e}")
            return []

    async def flush_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of keys deleted
        """
        try:
            keys = await self.keys(pattern)
            if keys:
                return await self.delete(*keys)
            return 0

        except Exception as e:
            print(f"Cache flush pattern error: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment integer value in cache.

        Args:
            key: Cache key
            amount: Amount to increment

        Returns:
            New value after increment
        """
        try:
            client = await self._get_client()
            return await client.incrby(key, amount)

        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0

    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement integer value in cache.

        Args:
            key: Cache key
            amount: Amount to decrement

        Returns:
            New value after decrement
        """
        try:
            client = await self._get_client()
            return await client.decrby(key, amount)

        except Exception as e:
            print(f"Cache decrement error: {e}")
            return 0

    async def set_hash(self, key: str, mapping: dict, expire: Optional[Union[int, timedelta]] = None) -> bool:
        """
        Set hash in cache.

        Args:
            key: Cache key
            mapping: Dictionary to store as hash
            expire: Expiration time

        Returns:
            True if successful
        """
        try:
            client = await self._get_client()
            await client.hset(key, mapping=mapping)

            if expire:
                await self.expire(key, expire)

            return True

        except Exception as e:
            print(f"Cache set hash error: {e}")
            return False

    async def get_hash(self, key: str, field: Optional[str] = None) -> Union[dict, str, None]:
        """
        Get hash or hash field from cache.

        Args:
            key: Cache key
            field: Specific field to get (optional)

        Returns:
            Hash dictionary, field value, or None
        """
        try:
            client = await self._get_client()

            if field:
                return await client.hget(key, field)
            else:
                return await client.hgetall(key)

        except Exception as e:
            print(f"Cache get hash error: {e}")
            return None


# Global cache manager instance
cache_manager = CacheManager()


# Convenience functions
async def cache_set(key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool:
    """Set value in cache."""
    return await cache_manager.set(key, value, expire)


async def cache_get(key: str, default: Any = None) -> Any:
    """Get value from cache."""
    return await cache_manager.get(key, default=default)


async def cache_delete(*keys: str) -> int:
    """Delete keys from cache."""
    return await cache_manager.delete(*keys)


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    return await cache_manager.exists(key)


def cache_key(*parts: str) -> str:
    """Generate cache key from parts."""
    return ":".join(str(part) for part in parts if part)