"""Celery tasks for ingestion workflows.

Tasks call the NVD client, parse records, convert to RDF and store them.
"""

from __future__ import annotations

import logging

from lib.celery_app import celery_app

from services.ingestion.nvd_client import NVDClient, parse_nvd_item
from services.rdf.serializer import store_vulnerability

logger = logging.getLogger(__name__)


@celery_app.task(name="wade.ingest.nvd")
def ingest_nvd_task(limit: int = 100):
    """Run a synchronous ingestion job to fetch and store NVD items.

    This task runs in the Celery worker process and uses the NVDClient to
    fetch items (async generator consumed via asyncio). For simplicity we run
    the async loop here.
    """
    import asyncio

    async def _run():
        client = NVDClient()
        count = 0
        async for raw in client.fetch_recent(limit=limit):
            try:
                v = parse_nvd_item(raw)
                inserted = store_vulnerability(v)
                # Count only newly inserted vulnerabilities
                if isinstance(inserted, int) and inserted > 0:
                    count += 1
            except Exception as e:
                logger.exception("Failed to ingest item: %s", e)
        return count

    total = asyncio.run(_run())
    logger.info("NVD ingestion completed, items=%d", total)
    return {"ingested": total}
