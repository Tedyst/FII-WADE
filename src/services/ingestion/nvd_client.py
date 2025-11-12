"""Simple NVD API client for fetching CVE data.

This is a minimal implementation to fetch recent CVEs and convert them
to the `Vulnerability` Pydantic model. It handles basic rate-limit backoff
and requires an optional API key via settings.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import AsyncIterator, Optional, List

from models.vulnerability import Vulnerability, SoftwareRef, Advisory
from lib.config import get_settings

logger = logging.getLogger(__name__)


class NVDClient:
    BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = getattr(settings, "nvd_api_key", None)
        # import httpx lazily to avoid requiring it at module import time (helps tests)
        import httpx

        self._client = httpx.AsyncClient(timeout=30)
        # Retry/backoff configuration
        self._max_retries = 3
        self._backoff_base = 1.0

    async def fetch_recent(self, limit: Optional[int] = None) -> AsyncIterator[dict]:
        """Yield raw CVE records from NVD. This is a generator to allow streaming.

        Args:
            limit: optional maximum number of items to fetch
        """
        params = {}
        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key

        # Basic pagination via startIndex / results per page
        start_index = 0
        per_page = 200
        fetched = 0

        while True:
            params.update({"startIndex": start_index, "resultsPerPage": per_page})
            try:
                resp = await self._request_with_retries(
                    "get", self.BASE, params=params, headers=headers
                )
            except Exception:
                # If repeated failures occur, stop iteration to avoid infinite loop
                logger.exception("NVD API repeated failures; aborting fetch_recent")
                break

            data = resp.json()
            cves = data.get("vulnerabilities") or data.get("result", {}).get("CVE_Items") or []

            if not cves:
                break

            for item in cves:
                yield item
                fetched += 1
                if limit and fetched >= limit:
                    await self._client.aclose()
                    return

            # advance
            start_index += per_page
            # simple termination guard
            total_results = data.get("totalResults") or data.get("result", {}).get("totalResults")
            if total_results and start_index >= int(total_results):
                break

        await self._client.aclose()

    async def fetch_parsed(self, limit: Optional[int] = None) -> AsyncIterator[Vulnerability]:
        """Yield parsed Vulnerability models from the NVD feed."""
        fetched = 0
        async for raw in self.fetch_recent(limit=limit):
            yield parse_nvd_item(raw)
            fetched += 1
            if limit and fetched >= limit:
                return

    async def fetch_batches(
        self, batch_size: int = 50, limit: Optional[int] = None
    ) -> AsyncIterator[List[Vulnerability]]:
        """Yield lists (batches) of parsed `Vulnerability` objects.

        This helps downstream ingestion to process batches and reduces transaction
        overhead when writing to stores.
        """
        batch: List[Vulnerability] = []
        count = 0
        async for v in self.fetch_parsed(limit=limit):
            batch.append(v)
            count += 1
            if len(batch) >= batch_size:
                yield batch
                batch = []
            if limit and count >= limit:
                break
        if batch:
            yield batch

    async def _request_with_retries(self, method: str, url: str, **kwargs):
        """Perform an HTTP request with basic retry + exponential backoff + jitter.

        Returns the response object on success or raises the last exception on failure.
        """
        last_exc = None
        for attempt in range(1, self._max_retries + 1):
            try:
                func = getattr(self._client, method)
                resp = await func(url, **kwargs)
                # raise for status to catch 4xx/5xx as exceptions
                resp.raise_for_status()
                return resp
            except Exception as exc:
                last_exc = exc
                # If response indicates 429, consider 'Retry-After' header
                try:
                    status = getattr(exc, "response", None) and getattr(
                        exc.response, "status_code", None
                    )
                except Exception:
                    status = None
                if attempt >= self._max_retries:
                    break
                backoff = self._backoff_base * (2 ** (attempt - 1))
                # add a small jitter
                backoff = backoff + random.uniform(0, 0.5 * backoff)
                logger.warning(
                    "Request failed (attempt %d/%d): %s; sleeping %.2fs",
                    attempt,
                    self._max_retries,
                    exc,
                    backoff,
                )
                await asyncio.sleep(backoff)

        # no success
        raise last_exc


def parse_nvd_item(raw: dict) -> Vulnerability:
    """Convert a raw NVD CVE item to our Vulnerability model.

    This is intentionally conservative: we map fields we expect and stash the raw
    payload for later processing.
    """
    # NVD uses nested structures; try to extract common fields
    cve_meta = raw.get("cve") or raw.get("vuln") or raw
    cve_id = None
    if isinstance(cve_meta, dict):
        cve_id = cve_meta.get("CVE_data_meta", {}).get("ID") or cve_meta.get("id")
    cve_id = cve_id or raw.get("id") or raw.get("cveId")

    description = None
    if isinstance(cve_meta, dict):
        descs = cve_meta.get("description", {}).get("description_data", [])
        if descs:
            description = descs[0].get("value")

    # CVSS extraction (best-effort)
    cvss_score = None
    cvss_vector = None
    impact = raw.get("impact") or {}
    try:
        # look for v3
        cvssv3 = impact.get("baseMetricV3") or {}
        if cvssv3:
            cvss_score = float(cvssv3.get("cvssV3", {}).get("baseScore"))
            cvss_vector = cvssv3.get("cvssV3", {}).get("vectorString")
    except Exception:
        pass

    # Affected software: parse CPE nodes conservatively
    affected = []
    nodes = raw.get("cpe", []) or raw.get("configurations", {}).get("nodes", [])
    # This is a placeholder; detailed CPE parsing lives in classifier
    for n in nodes:
        # try to extract product/vendor if present
        product = None
        vendor = None
        if isinstance(n, dict):
            for c in n.get("cpe_match", []) or n.get("cpe23Uri", []) or []:
                if isinstance(c, dict):
                    uri = c.get("cpe23Uri") or c.get("cpe_uri")
                else:
                    uri = c
                if uri and isinstance(uri, str):
                    # crude split
                    parts = uri.split(":")
                    if len(parts) >= 5:
                        vendor = parts[3]
                        product = parts[4]
                        affected.append(
                            SoftwareRef(name=product or uri, vendor=vendor, product=product)
                        )

    refs = []
    if isinstance(cve_meta, dict):
        refs = [
            r.get("url")
            for r in cve_meta.get("references", {}).get("reference_data", [])
            if r.get("url")
        ]

    vuln = Vulnerability(
        cveId=cve_id or "",
        description=description,
        cvss_score=cvss_score,
        cvss_vector=cvss_vector,
        affected=affected,
        references=refs,
        raw=raw,
    )

    return vuln
