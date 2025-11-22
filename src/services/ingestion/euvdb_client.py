"""EU Vulnerability DB client (placeholder).

This module provides a minimal EUVDB client implementation compatible with
the NVD client interface used by ingestion tasks. For now it exposes
`fetch_parsed` and `fetch_recent` generators and can be extended later.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator, List, Optional

from models.vulnerability import Vulnerability

logger = logging.getLogger(__name__)


class EUVDBClient:
    BASE = "https://example.euvdb.local/api"

    def __init__(self) -> None:
        # Lazy import httpx when needed
        self._client = None

    async def fetch_recent(self, limit: Optional[int] = None) -> AsyncIterator[dict]:
        """Yield raw records from EUVDB. Placeholder that yields nothing by default."""
        # Implement real HTTP fetching when API details are available.
        if False:
            yield {}
        return

    async def fetch_parsed(self, limit: Optional[int] = None) -> AsyncIterator[Vulnerability]:
        """Yield parsed Vulnerability models.

        Currently this is a placeholder to keep API compatibility with NVD client.
        """
        async for _ in self.fetch_recent(limit=limit):
            # conversion logic would go here
            continue
