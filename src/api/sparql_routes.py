from fastapi import APIRouter, Body, HTTPException, Request
import logging

from services.sparql.validator import validate_query
from services.sparql.endpoint import execute_sparql
from services.sparql.serializer import serialize_sparql_result
from lib.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sparql")
async def sparql_query(request: Request, query: str = Body(..., embed=True)):
    """Run a SPARQL query against the RDF store (read-only).

    Request body: { "query": "SELECT ..." }
    Supports content negotiation via `Accept` header for JSON/CSV/TSV.
    """
    ok, info = validate_query(query)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Invalid query: {info}")

    settings = get_settings()
    timeout = getattr(settings, "sparql_timeout", 10)

    # Determine preferred media type from Accept header (simple matching)
    accept = request.headers.get("accept", "")
    if "text/csv" in accept:
        media_type = "text/csv"
    elif "text/tab-separated-values" in accept or "text/tsv" in accept:
        media_type = "text/tab-separated-values"
    else:
        media_type = "application/sparql-results+json"

    try:
        result = await execute_sparql(query, timeout_seconds=timeout)
        # Use serializer to produce appropriate Response
        return serialize_sparql_result(result, media_type=media_type)
    except Exception as e:
        logger.exception("SPARQL execution failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
