from fastapi import APIRouter, Body, HTTPException
import logging

from services.sparql.validator import validate_query
from services.sparql.endpoint import execute_sparql
from lib.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sparql")
async def sparql_query(query: str = Body(..., embed=True)):
    """Run a SPARQL query against the RDF store (read-only).

    Request body: { "query": "SELECT ..." }
    """
    ok, info = validate_query(query)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Invalid query: {info}")

    settings = get_settings()
    timeout = getattr(settings, "sparql_timeout", 10)

    try:
        result = await execute_sparql(query, timeout_seconds=timeout)
        # If the result is a serialized string, return it as JSON
        if isinstance(result, str):
            return result
        return {"result": result}
    except Exception as e:
        logger.exception("SPARQL execution failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
