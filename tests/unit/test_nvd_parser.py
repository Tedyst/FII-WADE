from services.ingestion.nvd_client import parse_nvd_item


def make_sample_nvd_item():
    return {
        "cve": {
            "CVE_data_meta": {"ID": "CVE-2025-0002"},
            "description": {"description_data": [{"value": "Sample vulnerability"}]},
            "references": {"reference_data": [{"url": "https://example.org/ref"}]},
        },
        "impact": {
            "baseMetricV3": {
                "cvssV3": {"baseScore": 9.8, "vectorString": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}
            }
        },
        "configurations": {
            "nodes": [
                {"cpe_match": [{"cpe23Uri": "cpe:2.3:a:wordpress:wordpress:5.0:*:*:*:*:*:*:*"}]}
            ]
        },
    }


def test_parse_nvd_item_basic():
    raw = make_sample_nvd_item()
    v = parse_nvd_item(raw)
    assert v.cve_id == "CVE-2025-0002"
    assert "Sample vulnerability" in (v.description or "")
    assert v.cvss_score == 9.8
    assert len(v.affected) >= 1
