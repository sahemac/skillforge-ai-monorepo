"""
Redis cache configuration and utilities for Localization Service
"""

import json
from typing import Any, Optional
import redis.asyncio as redis
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    global redis_pool, redis_client

    if redis_client is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        redis_client = redis.Redis(connection_pool=redis_pool)

    return redis_client


async def close_redis():
    """Close Redis connections."""
    global redis_pool, redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None

    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None


async def cache_set(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Set a value in cache with optional expiration."""
    try:
        client = await get_redis()
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await client.set(key, serialized, ex=expire or settings.CACHE_TTL)
        return True
    except Exception as e:
        logger.error(f"Redis set error: {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache."""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    except Exception as e:
        logger.error(f"Redis get error: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """Delete a key from cache."""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis delete error: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    try:
        client = await get_redis()
        return bool(await client.exists(key))
    except Exception as e:
        logger.error(f"Redis exists error: {e}")
        return False