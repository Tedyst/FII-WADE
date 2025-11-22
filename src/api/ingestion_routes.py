from fastapi import APIRouter, HTTPException
import logging

from lib.config import get_settings

try:
    # import celery task if available
    from services.ingestion.tasks import ingest_nvd_task
except Exception:  # pragma: no cover - celery may not be available in tests
    ingest_nvd_task = None

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest/nvd")
async def ingest_nvd(limit: int = 100):
    """Trigger NVD ingestion. Uses Celery if configured, otherwise runs task inline."""
    settings = get_settings()
    if ingest_nvd_task is None:
        logger.info("Celery not available; running NVD ingestion inline")
        try:
            # call the task function directly (synchronous)
            result = ingest_nvd_task.run(limit=limit) if hasattr(ingest_nvd_task, "run") else None
            return {"status": "ok", "result": result}
        except Exception as e:
            logger.exception("Inline ingestion failed: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    # Enqueue Celery task
    try:
        job = ingest_nvd_task.delay(limit)
        return {"status": "enqueued", "task_id": job.id}
    except Exception as e:
        logger.exception("Failed to enqueue ingestion task: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/euvd")
async def ingest_euvd():
    """Placeholder endpoint to trigger EUVD ingestion in future.

    Currently this returns a 202 with a note that EUVD client is not implemented.
    """
    return {"status": "accepted", "message": "EUVDB ingestion not implemented yet"}
