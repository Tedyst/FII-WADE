"""Celery application configuration for asynchronous tasks.

Uses RabbitMQ as broker per research.md for multi-instance scalability.
"""

import logging

from celery import Celery

from lib.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "wade_vuln_dds",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["services.ingestion.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

logger.info("Celery app configured with broker: %s", settings.celery_broker_url)
