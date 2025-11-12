"""Convert Pydantic models into pyoxigraph quads/triples.

This module provides a small helper to convert `Vulnerability` instances into
pyoxigraph `Quad`s and insert them into the store.
"""

from __future__ import annotations

import logging
from urllib.parse import quote

from pyoxigraph import NamedNode, Literal, Quad

from models.vulnerability import Vulnerability
from lib.rdf_store import get_rdf_store
from lib.namespaces import VULN_NS, SCHEMA_NS, DCTERMS_NS, RDF, RDFS

logger = logging.getLogger(__name__)


def _vuln_uri(cve_id: str) -> NamedNode:
    safe = quote(cve_id, safe="")
    return NamedNode(f"http://wade.example.org/vuln/{safe}")


def vulnerability_to_quads(v: Vulnerability) -> list[Quad]:
    subj = _vuln_uri(v.cve_id)
    quads: list[Quad] = []

    # type triple
    quads.append(Quad(subj, NamedNode(RDF + "type"), VULN_NS.Vulnerability))

    # basic properties
    quads.append(Quad(subj, VULN_NS.cveId, Literal(v.cve_id)))
    if v.description:
        quads.append(Quad(subj, DCTERMS_NS.description, Literal(v.description)))
    if v.cvss_score is not None:
        quads.append(Quad(subj, VULN_NS.cvssScore, Literal(str(v.cvss_score))))

    # affected software as blank nodes
    for s in v.affected:
        # create a simple software node IRI using the name
        software_node = NamedNode(f"http://wade.example.org/software/{quote(s.name, safe='')}")
        quads.append(Quad(subj, VULN_NS.affectsSoftware, software_node))
        quads.append(Quad(software_node, SCHEMA_NS.name, Literal(s.name)))
        if s.category:
            quads.append(Quad(software_node, SCHEMA_NS.applicationCategory, Literal(s.category)))

    # advisories
    for a in v.advisories:
        adv_node = NamedNode(f"http://wade.example.org/advisory/{quote(a.id or v.cve_id, safe='')}")
        quads.append(Quad(subj, VULN_NS.hasAdvisory, adv_node))
        if a.title:
            quads.append(Quad(adv_node, DCTERMS_NS.title, Literal(a.title)))
        if a.url:
            quads.append(Quad(adv_node, DCTERMS_NS.identifier, Literal(a.url)))

    return quads


def store_vulnerability(v: Vulnerability) -> None:
    """Store a vulnerability in the RDF store with a simple deduplication
    check by `cve_id`. Returns the number of quads inserted (0 if already
    present or store unavailable).
    """
    try:
        store = get_rdf_store()
    except Exception:
        logger.info("RDF store unavailable; skipping storage for %s", v.cve_id)
        return 0

    # Try a lightweight existence check using SPARQL SELECT for the cveId
    try:
        query = f'SELECT ?s WHERE {{ ?s <{VULN_NS.cveId}> "{v.cve_id}" . }} LIMIT 1'
        try:
            res = store.query(query)
        except Exception:
            # In case pyoxigraph query isn't available or errors, fall back to insertion
            res = None

        exists = False
        if res is not None:
            # For pyoxigraph, query() on SELECT returns an iterator over dicts
            try:
                for _r in res:
                    exists = True
                    break
            except Exception:
                exists = False

        if exists:
            logger.info("Vulnerability %s already exists in store; skipping", v.cve_id)
            return 0

        quads = vulnerability_to_quads(v)
        for q in quads:
            store.add(q)
        logger.info("Inserted %d quads for %s", len(quads), v.cve_id)
        return len(quads)
    except Exception:
        logger.exception("Failed to store vulnerability %s", v.cve_id)
        return 0
