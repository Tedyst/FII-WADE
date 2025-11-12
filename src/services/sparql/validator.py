"""Basic SPARQL query validator to prevent destructive operations.

This is intentionally conservative: only allows SELECT/ASK/CONSTRUCT/DESCRIBE queries.
"""

import re
from typing import Tuple


ALLOWED = ("SELECT", "ASK", "CONSTRUCT", "DESCRIBE")


def validate_query(query: str) -> Tuple[bool, str]:
    if not query or not query.strip():
        return False, "Empty query"

    # Normalize
    q = query.strip().lstrip("(")
    m = re.match(r"^([A-Za-z]+)", q, re.IGNORECASE)
    if not m:
        return False, "Unable to determine query type"

    qtype = m.group(1).upper()
    if qtype not in ALLOWED:
        return False, f"Query type '{qtype}' not allowed"

    return True, qtype
