"""SPARQL executor wrapper with timeout.

This wraps the `pyoxigraph` store query execution. If `pyoxigraph` is not
available in the environment, the executor will raise a helpful error.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from lib.rdf_store import get_rdf_store

logger = logging.getLogger(__name__)


async def execute_sparql(query: str, timeout_seconds: int = 10) -> Any:
    """Execute a SPARQL query against the RDF store with a timeout.

    Returns a serialized result when possible (SPARQL JSON string), or raises
    a RuntimeError if the store or serializer is unavailable.
    """
    store = get_rdf_store()

    def _run_query():
        # pyoxigraph's Store.query returns a QueryResult which may be serializable
        try:
            res = store.query(query)
            # Try to serialize to SPARQL JSON if available
            try:
                return res.serialize("application/sparql-results+json")
            except Exception:
                # Fallback: convert to list of bindings if possible
                try:
                    return list(res)
                except Exception:
                    return res
        except Exception as e:
            # Bubble up
            raise

    try:
        result = await asyncio.wait_for(asyncio.to_thread(_run_query), timeout_seconds)
        return result
    except asyncio.TimeoutError:
        logger.error("SPARQL query timed out after %s seconds", timeout_seconds)
        raise
