import asyncio

from services.ingestion.nvd_client import NVDClient


def make_sample_nvd_item():
    return {
        "cve": {
            "CVE_data_meta": {"ID": "CVE-2025-9999"},
            "description": {"description_data": [{"value": "Transient sample"}]},
            "references": {"reference_data": [{"url": "https://example.org/ref"}]},
        },
        "impact": {
            "baseMetricV3": {
                "cvssV3": {"baseScore": 5.0, "vectorString": "AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N"}
            }
        },
        "configurations": {
            "nodes": [{"cpe_match": [{"cpe23Uri": "cpe:2.3:a:example:example:1.0:*:*:*:*:*:*:*"}]}]
        },
    }


def test_fetch_recent_retries(monkeypatch):
    # Create instance without running __init__ to avoid importing httpx in tests
    client = object.__new__(NVDClient)
    # set minimal attributes used by the methods under test
    client.api_key = None
    client._max_retries = 3
    client._backoff_base = 0.01

    calls = {"count": 0}

    async def fake_get(self, url, params=None, headers=None):
        calls["count"] += 1
        if calls["count"] == 1:
            # simulate a transient network error
            raise Exception("transient error")

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"vulnerabilities": [make_sample_nvd_item()]}

        return Resp()

    # attach a fake internal client with get and aclose
    async def fake_aclose(self=None):
        return None

    client._client = type("C", (), {"get": fake_get, "aclose": fake_aclose})()

    items = []

    async def run_fetch():
        async for it in client.fetch_recent(limit=1):
            items.append(it)

    asyncio.run(run_fetch())

    assert len(items) == 1
