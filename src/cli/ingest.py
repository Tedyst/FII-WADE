"""CLI ingestion helpers (stubs)
"""
import asyncio
import logging

logger = logging.getLogger(__name__)


async def _ingest_nvd_async():
    logger.info("Ingesting from NVD (stub)")


def ingest_nvd(args=None):
    """Start NVD ingestion (synchronous wrapper)."""
    asyncio.run(_ingest_nvd_async())


async def _ingest_euvd_async():
    logger.info("Ingesting from EUVD (stub)")


def ingest_euvd(args=None):
    asyncio.run(_ingest_euvd_async())
