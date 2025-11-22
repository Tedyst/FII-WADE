from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable, List, Mapping

from fastapi import Response


def _to_csv(bindings: Iterable[Mapping[str, Any]], delimiter: str = ",") -> str:
    # bindings is an iterable of dict-like rows
    buf = io.StringIO()
    rows = list(bindings)
    if not rows:
        return ""
    # header from first row keys
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    for r in rows:
        # ensure values are simple strings
        writer.writerow({k: (v if v is not None else "") for k, v in r.items()})
    return buf.getvalue()


def serialize_sparql_result(
    result: Any, media_type: str = "application/sparql-results+json"
) -> Response:
    """Return a FastAPI Response for a SPARQL query result.

    Accepts either a pyoxigraph serialization string, or an iterable of dicts.
    """
    # If result is already a string and media_type is JSON, return it
    if isinstance(result, str) and media_type == "application/sparql-results+json":
        return Response(content=result, media_type=media_type)

    # If result is list-like (bindings), serialize accordingly
    if isinstance(result, (list, tuple)):
        # produce JSON by default
        if media_type == "application/sparql-results+json":
            return Response(content=json.dumps(result), media_type=media_type)
        if media_type == "text/csv":
            csv_text = _to_csv(result, delimiter=",")
            return Response(content=csv_text, media_type="text/csv")
        if media_type == "text/tab-separated-values":
            tsv_text = _to_csv(result, delimiter="\t")
            return Response(content=tsv_text, media_type="text/tab-separated-values")

    # Fallback: JSON encode whatever we have
    return Response(content=json.dumps(result, default=str), media_type="application/json")
