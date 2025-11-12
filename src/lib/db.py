"""Database connection pool management using asyncpg.

Isolated database access per constitution's modular design principle.
"""

import logging
from typing import Optional

import asyncpg

from lib.config import get_settings

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    """Initialize the PostgreSQL connection pool.

    Returns:
        asyncpg connection pool

    Per constitution: Database access isolated to lib/db.py module
    """
    global _pool

    if _pool is not None:
        logger.warning("Database pool already initialized")
        return _pool

    settings = get_settings()
    logger.info(f"Initializing database connection pool: {settings.database_url}")

    try:
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        logger.info("Database pool initialized successfully")
        return _pool
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def get_db_pool() -> asyncpg.Pool:
    """Get the database connection pool.

    Returns:
        asyncpg connection pool

    Raises:
        RuntimeError: If pool not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


async def close_db_pool() -> None:
    """Close the database connection pool."""
    global _pool

    if _pool is not None:
        logger.info("Closing database connection pool")
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")
