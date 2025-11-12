# Implementation Plan: Vulnerability DDS with SPARQL Endpoint

**Branch**: `001-vuln-dds-sparql` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-vuln-dds-sparql/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a real-time Data Distribution Service (DDS) for web application vulnerability alerts using NVD API and EUVDB datasets. The system provides pub/sub notifications for security issues categorized by software class (CMS, frameworks, modules, shopping carts), a SPARQL endpoint for querying vulnerability solutions/advisories, multi-format output (HTML+RDFa, JSON-LD with schema.org), WebSub-compatible hub, and a smart caching proxy backed by Redis.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (API/proxy server), pyoxigraph (SPARQL/RDF storage), aiohttp (async HTTP client), redis-py (caching), pydantic (data validation)  
**Storage**: PostgreSQL (persistent metadata/subscriptions), pyoxigraph/oxigraph (RDF triple store for SPARQL), Redis (HTTP proxy cache)  
**Testing**: pytest, pytest-asyncio, httpx (async test client)  
**Target Platform**: Linux server (Docker containerized)  
**Project Type**: Single Python project with CLI entry point (main.py with argparse subcommands)  
**Performance Goals**: Handle 100+ concurrent subscribers, SPARQL queries <500ms p95, proxy cache hit ratio >70%  
**Constraints**: Extensible data source architecture (NVD + EUVDB initially), WebSub-compliant, schema.org vocabulary compatibility  
**Scale/Scope**: 10K+ vulnerability records, 50+ concurrent pub/sub connections, multi-tenant software class filtering

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS

Verifying compliance with [WADE Vulnerability DDS Constitution v1.0.0](../../.specify/memory/constitution.md):

| Principle | Compliance | Notes |
|-----------|-----------|-------|
| I. Simplicity First | ✅ PASS | Single Python project, standard libraries preferred, CLI-based design avoids unnecessary web frameworks for ingestion/admin tasks |
| II. Structured Logging | ✅ PASS | Plan mandates Python `logging` module throughout |
| III. Test Coverage | ✅ PASS | Project structure includes `tests/unit/`, `tests/integration/`, `tests/contract/` |
| IV. Modular Design | ✅ PASS | Services isolated (ingestion/, pubsub/, sparql/, proxy/), config externalized, BaseSource interface for extensibility |
| V. UX Consistency | ✅ PASS | CLI uses argparse subcommands, API uses FastAPI (standard REST), SPARQL follows W3C spec |
| Code Quality | ✅ PASS | Type hints, docstrings, PEP 8 planned |
| Performance | ✅ PASS | Goals align with constitution: <2s SPARQL queries, <500ms pubsub latency, 10 concurrent subscribers |
| Security | ✅ PASS | Input validation planned, rate limiting for ingestion, SPARQL timeout limits |

**No violations detected**. Will re-evaluate after Phase 1 design with concrete implementation details.

## Project Structure

### Documentation (this feature)

```text
specs/001-vuln-dds-sparql/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # REST API spec (pub/sub, SPARQL, proxy)
│   └── rdf-ontology.ttl # RDF/OWL vocabulary for vulnerabilities
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Pydantic models, RDF entity mappers
│   ├── vulnerability.py
│   ├── software.py
│   ├── advisory.py
│   └── subscription.py
├── services/            # Core business logic
│   ├── ingestion/
│   │   ├── nvd_client.py
│   │   ├── euvdb_client.py
│   │   └── base_source.py
│   ├── pubsub/
│   │   ├── broker.py
│   │   ├── websub_hub.py
│   │   └── subscriber.py
│   ├── sparql/
│   │   ├── endpoint.py
│   │   └── query_builder.py
│   ├── rdf/
│   │   ├── serializer.py
│   │   └── schema_org_mapper.py
│   └── proxy/
│       ├── cache_manager.py
│       └── proxy_handler.py
├── api/                 # FastAPI routes
│   ├── pubsub_routes.py
│   ├── sparql_routes.py
│   ├── proxy_routes.py
│   └── admin_routes.py
├── cli/                 # CLI subcommands
│   ├── api_server.py
│   ├── ingest.py
│   ├── client_sparql.py
│   └── admin.py
├── lib/                 # Shared utilities
│   ├── config.py
│   ├── db.py
│   └── logging.py
└── main.py              # Entry point with argparse

tests/
├── contract/            # API contract tests
├── integration/         # End-to-end flows
└── unit/                # Unit tests per module

docker/
├── docker-compose.yml   # PostgreSQL, Redis, Oxigraph services
├── Dockerfile           # Python app container
└── init-scripts/        # Database initialization

config/
├── settings.yaml        # Application configuration
└── ontology/            # RDF vocabularies
    └── vuln-ontology.ttl
```

**Structure Decision**: Single Python project structure chosen because all components (API, ingestion, SPARQL, proxy) share the same runtime and data models. CLI-based architecture with subcommands allows flexible deployment (run as server, batch ingestion, or client utilities).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
