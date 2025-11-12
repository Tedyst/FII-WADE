"""FastAPI application initialization.

Sets up middleware, exception handlers, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lib.config import get_settings
from lib.db import close_db_pool, init_db_pool
from lib.logging import setup_logging
from lib.rdf_store import close_rdf_store, init_rdf_store
from lib.redis_client import close_redis_client, init_redis_client
from api.sparql_routes import router as sparql_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Initializes and cleans up resources on startup/shutdown.
    """
    # Startup
    logger.info("Starting WADE Vulnerability DDS")
    settings = get_settings()
    setup_logging(settings.log_level)

    # Initialize infrastructure
    await init_db_pool()
    init_rdf_store()
    await init_redis_client()

    logger.info("All services initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down WADE Vulnerability DDS")
    await close_db_pool()
    close_rdf_store()
    await close_redis_client()
    logger.info("All services shut down successfully")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="WADE Vulnerability DDS",
        description="Data Distribution Service for web application vulnerabilities",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include SPARQL routes
    app.include_router(sparql_router)

    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler with logging per constitution."""
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create app instance
app = create_app()
