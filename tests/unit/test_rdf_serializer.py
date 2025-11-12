from models.vulnerability import Vulnerability, SoftwareRef
from services.rdf.serializer import store_vulnerability


def make_vulnerability() -> Vulnerability:
    return Vulnerability(
        cveId="CVE-2025-1000", description="Dedup test", affected=[SoftwareRef(name="example")]
    )


def test_store_vulnerability_skips_if_exists(monkeypatch):
    class FakeStoreExists:
        def query(self, q):
            # Simulate a single SELECT row indicating existence
            yield {"s": "http://wade.example.org/vuln/CVE-2025-1000"}

        def add(self, q):
            raise AssertionError("store.add should not be called when entry exists")

    monkeypatch.setattr("services.rdf.serializer.get_rdf_store", lambda: FakeStoreExists())

    count = store_vulnerability(make_vulnerability())
    assert count == 0


def test_store_vulnerability_inserts_if_not_exists(monkeypatch):
    added = []

    class FakeStoreNew:
        def query(self, q):
            # Return an empty iterator to indicate no existing rows
            return iter(())

        def add(self, q):
            added.append(q)

    monkeypatch.setattr("services.rdf.serializer.get_rdf_store", lambda: FakeStoreNew())

    count = store_vulnerability(make_vulnerability())
    assert count > 0
    assert len(added) == count
