"""Redis client manager for caching.

Per research.md: Redis for HTTP proxy cache and pub/sub coordination.
"""

import logging
from typing import Optional

import redis.asyncio as redis

from lib.config import get_settings

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def init_redis_client() -> redis.Redis:
    """Initialize the Redis client connection.

    Returns:
        Redis async client

    Per research.md: Redis for caching with TTL and pub/sub
    """
    global _redis_client

    if _redis_client is not None:
        logger.warning("Redis client already initialized")
        return _redis_client

    settings = get_settings()
    logger.info(f"Initializing Redis client: {settings.redis_url}")

    try:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await _redis_client.ping()
        logger.info("Redis client initialized successfully")
        return _redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {e}")
        raise


async def get_redis_client() -> redis.Redis:
    """Get the Redis client.

    Returns:
        Redis async client

    Raises:
        RuntimeError: If client not initialized
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis_client() first.")
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client connection."""
    global _redis_client

    if _redis_client is not None:
        logger.info("Closing Redis client")
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")
