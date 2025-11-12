"""pyoxigraph RDF store initialization and management.

Provides persistent RDF triple storage using RocksDB backend.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from pyoxigraph import Store
except Exception:  # pragma: no cover - optional dependency
    Store = None

from lib.config import get_settings

logger = logging.getLogger(__name__)

# Global RDF store instance
_store: Optional[object] = None


def init_rdf_store():
    """Initialize the pyoxigraph RDF store with RocksDB persistence.

    Returns:
        Initialized pyoxigraph Store

    Per research.md: pyoxigraph embedded with RocksDB for durability
    """
    global _store

    if _store is not None:
        logger.warning("RDF store already initialized")
        return _store

    settings = get_settings()
    if Store is None:
        raise RuntimeError("pyoxigraph is not installed; RDF store unavailable")

    store_path = Path(settings.oxigraph_dir)
    store_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Initializing RDF store at: {store_path}")

    try:
        _store = Store(str(store_path))
        logger.info("RDF store initialized successfully")
        return _store
    except Exception as e:
        logger.error(f"Failed to initialize RDF store: {e}")
        raise


def get_rdf_store():
    """Get the RDF store instance.

    Returns:
        pyoxigraph Store

    Raises:
        RuntimeError: If store not initialized
    """
    if _store is None:
        raise RuntimeError("RDF store not initialized. Call init_rdf_store() first.")
    return _store


def close_rdf_store() -> None:
    """Close the RDF store (flushes to disk)."""
    global _store

    if _store is not None:
        logger.info("Closing RDF store")
        # pyoxigraph Store automatically flushes on drop
        _store = None
        logger.info("RDF store closed")
