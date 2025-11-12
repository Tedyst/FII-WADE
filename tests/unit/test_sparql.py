import asyncio

from services.sparql.validator import validate_query
from services.sparql.endpoint import execute_sparql


def test_validate_query_allows_select():
    ok, qtype = validate_query("SELECT ?s WHERE { ?s ?p ?o }")
    assert ok and qtype == "SELECT"


def test_validate_query_rejects_update():
    ok, msg = validate_query("DROP SILENT GRAPH <http://example/>")
    assert not ok


def test_execute_sparql_with_mock_store(monkeypatch):
    # Create a dummy store whose query().serialize(...) returns a JSON string
    class DummyResult:
        def serialize(self, fmt):
            return '{"head":{}, "results":{}}'

    class DummyStore:
        def query(self, q):
            return DummyResult()

    # Patch the get_rdf_store used by the endpoint executor
    import services.sparql.endpoint as endpoint_module

    monkeypatch.setattr(endpoint_module, "get_rdf_store", lambda: DummyStore())

    res = asyncio.run(execute_sparql("SELECT ?s WHERE { ?s ?p ?o }", timeout_seconds=2))
    assert isinstance(res, str)
    assert "head" in res
