from datetime import date

from models.vulnerability import Vulnerability, SoftwareRef, Advisory


def test_vulnerability_model_basic():
    s = SoftwareRef(
        name="ExampleCMS", vendor="example", product="examplecms", version="1.2.3", category="CMS"
    )
    a = Advisory(
        id="ADV-1",
        title="Fix available",
        text="Update plugin",
        url="https://example.org/adv/1",
        published_by="Vendor",
    )
    v = Vulnerability(
        cveId="CVE-2025-0001",
        description="Test vuln",
        cvss_score=7.5,
        cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        published_date=date(2025, 1, 1),
        affected=[s],
        references=["https://nvd.nist.gov"],
        advisories=[a],
    )

    assert v.cve_id == "CVE-2025-0001"
    assert v.affected[0].name == "ExampleCMS"
    assert v.advisories[0].title == "Fix available"
