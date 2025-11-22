````markdown
# Tasks: Vulnerability DDS with SPARQL Endpoint

**Input**: Design documents from `/specs/001-vuln-dds-sparql/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as per constitution requirement (70% coverage minimum)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/models/, src/services/, src/api/, src/cli/, src/lib/, tests/)
- [x] T002 Initialize pyproject.toml with project metadata and dependencies (fastapi, pyoxigraph, celery, aiohttp, asyncpg, redis, pydantic, jinja2)
- [x] T003 [P] Create Docker Compose orchestration in docker/docker-compose.yml for postgres, redis, rabbitmq, oxigraph services
- [x] T004 [P] Create Dockerfile for Python app container with uv package manager
- [x] T005 [P] Create .env.example with environment variable templates (DATABASE_URL, REDIS_URL, RABBITMQ_URL, NVD_API_KEY)
- [x] T006 [P] Create src/lib/config.py for loading configuration from environment and YAML files
- [x] T007 [P] Configure Python logging in src/lib/logging.py with structured format per constitution
- [x] T008 [P] Create database schema initialization script in docker/init-scripts/init_db.sql for subscriptions table
- [x] T009 [P] Create config/settings.yaml with cache TTLs, performance limits, software class mappings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create base Pydantic models in src/models/**init**.py (import structure)
- [x] T011 [P] Implement database connection pool in src/lib/db.py using asyncpg
- [x] T012 [P] Create pyoxigraph store initialization in src/lib/rdf_store.py with RocksDB backend
- [x] T013 [P] Implement base data source interface in src/services/ingestion/base_source.py (abstract class with fetch_vulnerabilities, parse_record, get_software_class methods)
- [x] T014 [P] Create RDF namespace definitions in src/lib/namespaces.py (vuln:, schema:, dcterms:)
- [x] T015 [P] Implement CPE to software class mapping in src/services/classification/cpe_classifier.py
- [x] T016 [P] Configure Celery app in src/lib/celery_app.py with RabbitMQ broker
- [x] T017 [P] Create FastAPI app initialization in src/api/app.py with middleware, exception handlers
- [x] T018 [P] Implement Redis connection manager in src/lib/redis_client.py
- [x] T019 Create main CLI entry point in src/main.py with argparse subcommands

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Data Ingestion from Vulnerability Sources (Priority: P1) 🎯 MVP

**Goal**: Automatically ingest vulnerability data from NVD and EUVD APIs and store in RDF format

**Independent Test**: Run `python -m src.main ingest-nvd` and `python -m src.main ingest-euvd`, then execute SPARQL query to verify CVE records are stored correctly

### Tests for User Story 1

- [x] T020 [P] [US1] Create unit test for NVD client in tests/unit/test_nvd_client.py (mock API responses)
- [ ] T021 [P] [US1] Create unit test for EUVD client in tests/unit/test_euvd_client.py (mock API responses)
- [x] T022 [P] [US1] Create unit test for RDF serializer in tests/unit/test_rdf_serializer.py
- [ ] T023 [US1] Create integration test for ingestion pipeline in tests/integration/test_ingestion_flow.py

### Implementation for User Story 1

- [x] T024 [P] [US1] Create Vulnerability Pydantic model in src/models/vulnerability.py with validation
- [x] T025 [P] [US1] Create SoftwareRef Pydantic model in src/models/software.py
- [x] T026 [P] [US1] Create Advisory Pydantic model in src/models/advisory.py
- [x] T027 [US1] Implement NVD API client in src/services/ingestion/nvd_client.py (fetch CVEs, handle rate limits, API key auth)
- [x] T028 [US1] Implement EUVD API client in src/services/ingestion/euvdb_client.py (fetch from /lastvulnerabilities, /criticalvulnerabilities, /search endpoints)
- [x] T029 [US1] Implement RDF triple converter in src/services/rdf/serializer.py (Pydantic → pyoxigraph.Quad)
- [ ] T030 [US1] Implement schema.org mapper in src/services/rdf/schema_org_mapper.py (map to SoftwareApplication/TechArticle)
- [x] T031 [US1] Create Celery task for NVD ingestion in src/services/ingestion/tasks.py (async background job)
- [x] T032 [US1] Create Celery task for EUVD ingestion in src/services/ingestion/tasks.py
- [x] T033 [US1] Implement CLI command handler in src/cli/ingest.py for ingest-nvd and ingest-euvd
- [x] T034 [US1] Add ingestion endpoints to FastAPI in src/api/ingestion_routes.py (POST /ingest/nvd, POST /ingest/euvd)
- [x] T035 [US1] Add duplicate detection logic using SPARQL queries before inserting RDF triples
- [ ] T036 [US1] Add comprehensive logging for ingestion operations per constitution

**Checkpoint**: At this point, User Story 1 should be fully functional - CVE data can be ingested and stored in RDF format

---

## Phase 4: User Story 2 - SPARQL Query Endpoint (Priority: P2)

**Goal**: Expose SPARQL endpoint for querying vulnerability data with timeout enforcement

**Independent Test**: Start API server, POST SPARQL query to `/sparql`, verify SPARQL JSON results are returned correctly

### Tests for User Story 2

- [ ] T037 [P] [US2] Create contract test for SPARQL endpoint in tests/contract/test_sparql_api.py
- [ ] T038 [P] [US2] Create unit test for query timeout in tests/unit/test_sparql_timeout.py
- [ ] T039 [P] [US2] Create integration test for complex SPARQL queries in tests/integration/test_sparql_queries.py

### Implementation for User Story 2

- [x] T040 [P] [US2] Create SPARQL query validator in src/services/sparql/validator.py (sanitize input, prevent injection)
- [x] T041 [P] [US2] Implement SPARQL query executor in src/services/sparql/endpoint.py with 10-second timeout
- [x] T042 [P] [US2] Implement query result serializer in src/services/sparql/serializer.py (to SPARQL JSON, CSV, TSV)
- [x] T043 [P] [US2] Create FastAPI SPARQL routes in src/api/sparql_routes.py (POST /sparql accepting application/sparql-query)
- [x] T044 [US2] Add content negotiation for result formats (application/sparql-results+json, text/csv)
- [x] T045 [US2] Implement CLI SPARQL client in src/cli/client_sparql.py (send query to endpoint, display results)
- [ ] T046 [US2] Add query performance logging and metrics collection

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - data can be ingested and queried via SPARQL

---

## Phase 5: User Story 3 - Real-Time Pub/Sub Alerts (Priority: P3)

**Goal**: Enable real-time vulnerability notifications via webhooks and SSE for specific software classes

**Independent Test**: Subscribe to topic, ingest new vulnerability, verify notification received within 500ms

### Tests for User Story 3

- [ ] T047 [P] [US3] Create unit test for RabbitMQ broker in tests/unit/test_pubsub_broker.py
- [ ] T048 [P] [US3] Create unit test for subscription filtering in tests/unit/test_subscription_filter.py
- [ ] T049 [US3] Create integration test for pub/sub flow in tests/integration/test_pubsub_notifications.py

### Implementation for User Story 3

- [ ] T050 [P] [US3] Create Subscription Pydantic model in src/models/subscription.py with filters
- [ ] T051 [P] [US3] Implement subscription repository in src/services/pubsub/subscription_repo.py (PostgreSQL CRUD)
- [ ] T052 [US3] Implement RabbitMQ publisher in src/services/pubsub/publisher.py (publish to topics by software class)
- [ ] T053 [US3] Implement RabbitMQ consumer in src/services/pubsub/consumer.py (consume and route to subscribers)
- [ ] T054 [US3] Implement webhook notification delivery in src/services/pubsub/webhook_sender.py (POST to callback URLs with retry logic)
- [ ] T055 [US3] Implement SSE handler in src/api/sse_routes.py (GET /stream/vulnerabilities with query params)
- [ ] T056 [US3] Create subscription management routes in src/api/subscription_routes.py (POST /subscriptions, GET /subscriptions, DELETE /subscriptions/{id})
- [ ] T057 [US3] Integrate publisher into ingestion pipeline (publish after storing RDF triples)
- [ ] T058 [US3] Implement subscription filtering (by software class, CVSS score, CWE category)
- [ ] T059 [US3] Add notification delivery logging and failure tracking

**Checkpoint**: All core features functional - ingestion, querying, and real-time alerts work independently

---

## Phase 6: User Story 4 - WebSub Hub Implementation (Priority: P4)

**Goal**: Implement W3C WebSub protocol for federated subscription model

**Independent Test**: Perform WebSub subscription handshake, publish content, verify callback receives notification

### Tests for User Story 4

- [ ] T060 [P] [US4] Create contract test for WebSub hub in tests/contract/test_websub_hub.py
- [ ] T061 [US4] Create integration test for WebSub workflow in tests/integration/test_websub_subscription.py

### Implementation for User Story 4

- [ ] T062 [P] [US4] Implement WebSub subscription verification in src/services/pubsub/websub_verifier.py (challenge token)
- [ ] T063 [P] [US4] Implement WebSub hub logic in src/services/pubsub/websub_hub.py (subscription management, content distribution)
- [ ] T064 [US4] Create WebSub hub routes in src/api/websub_routes.py (POST /websub/hub for hub.mode=subscribe/unsubscribe/publish)
- [ ] T065 [US4] Add subscription lease expiry tracking and renewal reminders
- [ ] T066 [US4] Integrate WebSub hub with RabbitMQ publisher for content distribution
- [ ] T067 [US4] Add WebSub-specific logging and subscription status tracking

**Checkpoint**: WebSub protocol fully functional alongside existing pub/sub mechanisms

---

## Phase 7: User Story 5 - Multi-Format Output (HTML+RDFa, JSON-LD) (Priority: P5)

**Goal**: Provide vulnerability data in HTML+RDFa and JSON-LD formats with schema.org vocabulary

**Independent Test**: Request vulnerability by CVE ID with different Accept headers, validate HTML+RDFa and JSON-LD output

### Tests for User Story 5

- [ ] T068 [P] [US5] Create unit test for HTML+RDFa generator in tests/unit/test_rdfa_generator.py
- [ ] T069 [P] [US5] Create unit test for JSON-LD serializer in tests/unit/test_jsonld_serializer.py
- [ ] T070 [P] [US5] Create integration test for content negotiation in tests/integration/test_content_negotiation.py

### Implementation for User Story 5

- [ ] T071 [P] [US5] Create Jinja2 HTML+RDFa template in src/templates/vulnerability.html with schema.org annotations
- [ ] T072 [P] [US5] Implement HTML+RDFa generator in src/services/output/rdfa_generator.py
- [ ] T073 [P] [US5] Implement JSON-LD serializer in src/services/output/jsonld_serializer.py with schema.org context
- [ ] T074 [US5] Create vulnerability detail routes in src/api/vulnerability_routes.py (GET /vulnerabilities/{cve_id})
- [ ] T075 [US5] Implement content negotiation based on Accept header (text/html, application/ld+json)
- [ ] T076 [US5] Add schema.org vocabulary mapping for SoftwareApplication, SoftwareSourceCode, TechArticle
- [ ] T077 [US5] Validate JSON-LD output against schema.org schemas

**Checkpoint**: Multi-format output operational - vulnerability data accessible as HTML+RDFa and JSON-LD

---

## Phase 8: User Story 6 - Smart Caching Proxy (Priority: P6)

**Goal**: Implement Redis-backed HTTP caching proxy with heuristic TTLs

**Independent Test**: Make repeated requests to proxied endpoints, verify cache hits and >70% hit rate after warm-up

### Tests for User Story 6

- [ ] T078 [P] [US6] Create unit test for cache key generation in tests/unit/test_cache_keys.py
- [ ] T079 [P] [US6] Create unit test for TTL heuristics in tests/unit/test_cache_ttl.py
- [ ] T080 [US6] Create integration test for proxy caching in tests/integration/test_proxy_cache.py

### Implementation for User Story 6

- [ ] T081 [P] [US6] Implement cache key generator in src/services/proxy/cache_key.py (hash URL + params)
- [ ] T082 [P] [US6] Implement cache manager in src/services/proxy/cache_manager.py (Redis get/set with TTL)
- [ ] T083 [P] [US6] Implement TTL heuristics in src/services/proxy/ttl_calculator.py (CVE=24h, exploit=1h, SPARQL=5min)
- [ ] T084 [US6] Implement HTTP proxy handler in src/services/proxy/proxy_handler.py with httpx.AsyncClient
- [ ] T085 [US6] Create proxy routes in src/api/proxy_routes.py (GET /proxy/{path:path})
- [ ] T086 [US6] Add X-Cache header to responses (HIT/MISS)
- [ ] T087 [US6] Implement cache invalidation on ingestion updates
- [ ] T088 [US6] Add cache hit rate metrics and logging
- [ ] T089 [US6] Implement graceful degradation when Redis unavailable

**Checkpoint**: All user stories complete - full system functional with caching optimization

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T090 [P] Create comprehensive README.md with setup, usage examples, architecture diagram
- [ ] T091 [P] Add --help documentation for all CLI subcommands
- [ ] T092 [P] Create example SPARQL queries in docs/examples/sparql_queries.md
- [ ] T093 [P] Create demo subscriber client in src/cli/demo_subscriber.py (receives webhooks)
- [ ] T094 [P] Add Prometheus metrics endpoint in src/api/metrics_routes.py (optional)
- [ ] T095 [P] Run black formatter on all Python files per constitution
- [ ] T096 [P] Run mypy type checking on all source files
- [ ] T097 [P] Add API documentation using FastAPI's automatic OpenAPI generation
- [ ] T098 [P] Create troubleshooting guide in docs/troubleshooting.md
- [ ] T099 Validate quickstart.md instructions by running from scratch
- [ ] T100 Run full test suite and verify 70%+ coverage per constitution
- [ ] T101 Security audit: validate input sanitization, rate limiting, query timeouts
- [ ] T102 Performance testing: verify success criteria (SC-001 through SC-010) are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Ingestion: No dependencies on other stories
  - User Story 2 (P2) - SPARQL: Depends on US1 data being available (but can develop in parallel with mock data)
  - User Story 3 (P3) - Pub/Sub: Depends on US1 ingestion triggering notifications
  - User Story 4 (P4) - WebSub: Builds on US3 pub/sub infrastructure
  - User Story 5 (P5) - Multi-format: Depends on US1 data and US2 SPARQL endpoint
  - User Story 6 (P6) - Caching: Can wrap any existing endpoints (minimal dependencies)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Ingestion)**: Independent - can complete fully without other stories
- **US2 (SPARQL)**: Independent - can complete with US1 data or test fixtures
- **US3 (Pub/Sub)**: Requires US1 ingestion to trigger notifications
- **US4 (WebSub)**: Extends US3 pub/sub with WebSub protocol
- **US5 (Multi-format)**: Requires US1 data; benefits from US2 SPARQL but not required
- **US6 (Caching)**: Independent - wraps existing endpoints

### Within Each User Story

- Tests FIRST → Models → Services → API Routes → Integration
- All [P] tasks within a phase can run in parallel
- Core implementation before cross-story integration

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006, T007, T008, T009 can all run in parallel
- **Phase 2 (Foundational)**: T011-T018 can all run in parallel after T010
- **Phase 3 (US1)**: T020-T022 tests in parallel; T024-T026 models in parallel
- **User Stories**: US1, US2, US6 can be developed in parallel by different developers
- **Phase 9 (Polish)**: Most tasks T090-T098 can run in parallel

---

## Parallel Example: User Story 1 (Ingestion)

```bash
# Launch all tests together:
Parallel batch 1:
- T020: Unit test for NVD client
- T021: Unit test for EUVD client
- T022: Unit test for RDF serializer

# Launch all models together:
Parallel batch 2:
- T024: Vulnerability model
- T025: SoftwareRef model
- T026: Advisory model

# Sequential after models complete:
- T027: NVD client (uses T024, T025)
- T028: EUVD client (uses T024, T025)
- T029: RDF serializer (uses T024, T025, T026)
# ... continue with remaining tasks
```
````

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T019) - **CRITICAL CHECKPOINT**
3. Complete Phase 3: User Story 1 - Ingestion (T020-T036)
4. **VALIDATE US1**: Ingest sample CVEs, verify RDF storage
5. Complete Phase 4: User Story 2 - SPARQL (T037-T046)
6. **VALIDATE US2**: Query ingested data via SPARQL endpoint
7. **DEMO READY**: MVP with ingestion + querying functional

### Incremental Delivery

1. MVP (US1 + US2) → Deploy/Demo
2. Add US3 (Pub/Sub) → Test independently → Deploy/Demo
3. Add US4 (WebSub) → Test independently → Deploy/Demo
4. Add US5 (Multi-format) → Test independently → Deploy/Demo
5. Add US6 (Caching) → Test independently → Deploy/Demo
6. Polish (Phase 9) → Final release

### Parallel Team Strategy

With 3 developers after Foundational phase complete:

- **Developer A**: US1 (Ingestion) + US3 (Pub/Sub)
- **Developer B**: US2 (SPARQL) + US5 (Multi-format)
- **Developer C**: US4 (WebSub) + US6 (Caching)

---

## Summary

- **Total Tasks**: 102
- **Setup Tasks**: 9 (Phase 1)
- **Foundational Tasks**: 10 (Phase 2)
- **User Story Tasks**: 70 (Phases 3-8)
  - US1 (Ingestion): 17 tasks
  - US2 (SPARQL): 10 tasks
  - US3 (Pub/Sub): 13 tasks
  - US4 (WebSub): 8 tasks
  - US5 (Multi-format): 10 tasks
  - US6 (Caching): 12 tasks
- **Polish Tasks**: 13 (Phase 9)
- **Parallelizable Tasks**: 45 marked with [P]
- **MVP Scope**: Phases 1, 2, 3, 4 (T001-T046) = 46 tasks

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] marker indicates tasks that can run in parallel (different files, no blocking dependencies)
- [Story] marker (US1-US6) maps tasks to user stories for traceability
- Each user story phase delivers independently testable functionality
- Tests included per constitution requirement (70% coverage minimum)
- Constitution compliance: structured logging, type hints, docstrings, PEP 8 enforced
- Stop at any checkpoint to validate story independently before proceeding

````
# Tasks: Vulnerability DDS with SPARQL Endpoint

**Input**: Design documents from `/specs/001-vuln-dds-sparql/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as per constitution requirement (70% coverage minimum)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

 - [X] T001 Create project directory structure per plan.md (src/models/, src/services/, src/api/, src/cli/, src/lib/, tests/)
 - [X] T002 Initialize pyproject.toml with project metadata and dependencies (fastapi, pyoxigraph, celery, aiohttp, asyncpg, redis, pydantic, jinja2)
 - [X] T003 [P] Create Docker Compose orchestration in docker/docker-compose.yml for postgres, redis, rabbitmq, oxigraph services
 - [X] T004 [P] Create Dockerfile for Python app container with uv package manager
 - [X] T005 [P] Create .env.example with environment variable templates (DATABASE_URL, REDIS_URL, RABBITMQ_URL, NVD_API_KEY)
 - [X] T006 [P] Create src/lib/config.py for loading configuration from environment and YAML files
 - [X] T007 [P] Configure Python logging in src/lib/logging.py with structured format per constitution
 - [X] T008 [P] Create database schema initialization script in docker/init-scripts/init_db.sql for subscriptions table
 - [X] T009 [P] Create config/settings.yaml with cache TTLs, performance limits, software class mappings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

 - [X] T010 Create base Pydantic models in src/models/**init**.py (import structure)
 - [X] T011 [P] Implement database connection pool in src/lib/db.py using asyncpg
 - [X] T012 [P] Create pyoxigraph store initialization in src/lib/rdf_store.py with RocksDB backend
 - [X] T013 [P] Implement base data source interface in src/services/ingestion/base_source.py (abstract class with fetch_vulnerabilities, parse_record, get_software_class methods)
 - [X] T014 [P] Create RDF namespace definitions in src/lib/namespaces.py (vuln:, schema:, dcterms:)
 - [X] T015 [P] Implement CPE to software class mapping in src/services/classification/cpe_classifier.py
 - [X] T016 [P] Configure Celery app in src/lib/celery_app.py with RabbitMQ broker
 - [X] T017 [P] Create FastAPI app initialization in src/api/app.py with middleware, exception handlers
 - [X] T018 [P] Implement Redis connection manager in src/lib/redis_client.py
 - [X] T019 Create main CLI entry point in src/main.py with argparse subcommands

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Data Ingestion from Vulnerability Sources (Priority: P1) 🎯 MVP

**Goal**: Automatically ingest vulnerability data from NVD and EUVD APIs and store in RDF format

**Independent Test**: Run `python -m src.main ingest-nvd` and `python -m src.main ingest-euvd`, then execute SPARQL query to verify CVE records are stored correctly

 ### Tests for User Story 2

  - [ ] T037 [P] [US2] Create contract test for SPARQL endpoint in tests/contract/test_sparql_api.py
  - [ ] T038 [P] [US2] Create unit test for query timeout in tests/unit/test_sparql_timeout.py
  - [ ] T039 [P] [US2] Create integration test for complex SPARQL queries in tests/integration/test_sparql_queries.py
 - [ ] T023 [US1] Create integration test for ingestion pipeline in tests/integration/test_ingestion_flow.py

### Implementation for User Story 1

 - [X] T024 [P] [US1] Create Vulnerability Pydantic model in src/models/vulnerability.py with validation
 - [ ] T025 [P] [US1] Create SoftwareRef Pydantic model in src/models/software.py
 - [ ] T026 [P] [US1] Create Advisory Pydantic model in src/models/advisory.py
 - [X] T027 [US1] Implement NVD API client in src/services/ingestion/nvd_client.py (fetch CVEs, handle rate limits, API key auth)
 - [ ] T028 [US1] Implement EUVD API client in src/services/ingestion/euvdb_client.py (fetch from /lastvulnerabilities, /criticalvulnerabilities, /search endpoints)
 - [X] T029 [US1] Implement RDF triple converter in src/services/rdf/serializer.py (Pydantic → pyoxigraph.Quad)
 - [ ] T030 [US1] Implement schema.org mapper in src/services/rdf/schema_org_mapper.py (map to SoftwareApplication/TechArticle)
 - [X] T031 [US1] Create Celery task for NVD ingestion in src/services/ingestion/tasks.py (async background job)
 - [X] T032 [US1] Create Celery task for EUVD ingestion in src/services/ingestion/tasks.py
 - [X] T033 [US1] Implement CLI command handler in src/cli/ingest.py for ingest-nvd and ingest-euvd
 - [ ] T034 [US1] Add ingestion endpoints to FastAPI in src/api/ingestion_routes.py (POST /ingest/nvd, POST /ingest/euvd)
 - [ ] T035 [US1] Add duplicate detection logic using SPARQL queries before inserting RDF triples
 - [ ] T036 [US1] Add comprehensive logging for ingestion operations per constitution

**Checkpoint**: At this point, User Story 1 should be fully functional - CVE data can be ingested and stored in RDF format

---

## Phase 4: User Story 2 - SPARQL Query Endpoint (Priority: P2)

**Goal**: Expose SPARQL endpoint for querying vulnerability data with timeout enforcement

**Independent Test**: Start API server, POST SPARQL query to `/sparql`, verify SPARQL JSON results are returned correctly

### Tests for User Story 2



### Implementation for User Story 2

 - [X] T040 [P] [US2] Create SPARQL query validator in src/services/sparql/validator.py (sanitize input, prevent injection)
 - [X] T041 [P] [US2] Implement SPARQL query executor in src/services/sparql/endpoint.py with 10-second timeout
 - [X] T043 [P] [US2] Create FastAPI SPARQL routes in src/api/sparql_routes.py (POST /sparql accepting application/sparql-query)
 - [X] T045 [US2] Implement CLI SPARQL client in src/cli/client_sparql.py (send query to endpoint, display results)
---

## Phase 5: User Story 3 - Real-Time Pub/Sub Alerts (Priority: P3)

**Goal**: Enable real-time vulnerability notifications via webhooks and SSE for specific software classes

**Independent Test**: Subscribe to topic, ingest new vulnerability, verify notification received within 500ms

### Tests for User Story 3

- [ ] T047 [P] [US3] Create unit test for RabbitMQ broker in tests/unit/test_pubsub_broker.py
- [ ] T048 [P] [US3] Create unit test for subscription filtering in tests/unit/test_subscription_filter.py
- [ ] T049 [US3] Create integration test for pub/sub flow in tests/integration/test_pubsub_notifications.py

### Implementation for User Story 3

- [ ] T050 [P] [US3] Create Subscription Pydantic model in src/models/subscription.py with filters
- [ ] T051 [P] [US3] Implement subscription repository in src/services/pubsub/subscription_repo.py (PostgreSQL CRUD)
- [ ] T052 [US3] Implement RabbitMQ publisher in src/services/pubsub/publisher.py (publish to topics by software class)
- [ ] T053 [US3] Implement RabbitMQ consumer in src/services/pubsub/consumer.py (consume and route to subscribers)
- [ ] T054 [US3] Implement webhook notification delivery in src/services/pubsub/webhook_sender.py (POST to callback URLs with retry logic)
- [ ] T055 [US3] Implement SSE handler in src/api/sse_routes.py (GET /stream/vulnerabilities with query params)
- [ ] T056 [US3] Create subscription management routes in src/api/subscription_routes.py (POST /subscriptions, GET /subscriptions, DELETE /subscriptions/{id})
- [ ] T057 [US3] Integrate publisher into ingestion pipeline (publish after storing RDF triples)
- [ ] T058 [US3] Implement subscription filtering (by software class, CVSS score, CWE category)
- [ ] T059 [US3] Add notification delivery logging and failure tracking

**Checkpoint**: All core features functional - ingestion, querying, and real-time alerts work independently

---

## Phase 6: User Story 4 - WebSub Hub Implementation (Priority: P4)

**Goal**: Implement W3C WebSub protocol for federated subscription model

**Independent Test**: Perform WebSub subscription handshake, publish content, verify callback receives notification

### Tests for User Story 4

- [ ] T060 [P] [US4] Create contract test for WebSub hub in tests/contract/test_websub_hub.py
- [ ] T061 [US4] Create integration test for WebSub workflow in tests/integration/test_websub_subscription.py

### Implementation for User Story 4

- [ ] T062 [P] [US4] Implement WebSub subscription verification in src/services/pubsub/websub_verifier.py (challenge token)
- [ ] T063 [P] [US4] Implement WebSub hub logic in src/services/pubsub/websub_hub.py (subscription management, content distribution)
- [ ] T064 [US4] Create WebSub hub routes in src/api/websub_routes.py (POST /websub/hub for hub.mode=subscribe/unsubscribe/publish)
- [ ] T065 [US4] Add subscription lease expiry tracking and renewal reminders
- [ ] T066 [US4] Integrate WebSub hub with RabbitMQ publisher for content distribution
- [ ] T067 [US4] Add WebSub-specific logging and subscription status tracking

**Checkpoint**: WebSub protocol fully functional alongside existing pub/sub mechanisms

---

## Phase 7: User Story 5 - Multi-Format Output (HTML+RDFa, JSON-LD) (Priority: P5)

**Goal**: Provide vulnerability data in HTML+RDFa and JSON-LD formats with schema.org vocabulary

**Independent Test**: Request vulnerability by CVE ID with different Accept headers, validate HTML+RDFa and JSON-LD output

### Tests for User Story 5

- [ ] T068 [P] [US5] Create unit test for HTML+RDFa generator in tests/unit/test_rdfa_generator.py
- [ ] T069 [P] [US5] Create unit test for JSON-LD serializer in tests/unit/test_jsonld_serializer.py
- [ ] T070 [US5] Create integration test for content negotiation in tests/integration/test_content_negotiation.py

### Implementation for User Story 5

- [ ] T071 [P] [US5] Create Jinja2 HTML+RDFa template in src/templates/vulnerability.html with schema.org annotations
- [ ] T072 [P] [US5] Implement HTML+RDFa generator in src/services/output/rdfa_generator.py
- [ ] T073 [P] [US5] Implement JSON-LD serializer in src/services/output/jsonld_serializer.py with schema.org context
- [ ] T074 [US5] Create vulnerability detail routes in src/api/vulnerability_routes.py (GET /vulnerabilities/{cve_id})
- [ ] T075 [US5] Implement content negotiation based on Accept header (text/html, application/ld+json)
- [ ] T076 [US5] Add schema.org vocabulary mapping for SoftwareApplication, SoftwareSourceCode, TechArticle
- [ ] T077 [US5] Validate JSON-LD output against schema.org schemas

**Checkpoint**: Multi-format output operational - vulnerability data accessible as HTML+RDFa and JSON-LD

---

## Phase 8: User Story 6 - Smart Caching Proxy (Priority: P6)

**Goal**: Implement Redis-backed HTTP caching proxy with heuristic TTLs

**Independent Test**: Make repeated requests to proxied endpoints, verify cache hits and >70% hit rate after warm-up

### Tests for User Story 6

- [ ] T078 [P] [US6] Create unit test for cache key generation in tests/unit/test_cache_keys.py
- [ ] T079 [P] [US6] Create unit test for TTL heuristics in tests/unit/test_cache_ttl.py
- [ ] T080 [US6] Create integration test for proxy caching in tests/integration/test_proxy_cache.py

### Implementation for User Story 6

- [ ] T081 [P] [US6] Implement cache key generator in src/services/proxy/cache_key.py (hash URL + params)
- [ ] T082 [P] [US6] Implement cache manager in src/services/proxy/cache_manager.py (Redis get/set with TTL)
- [ ] T083 [P] [US6] Implement TTL heuristics in src/services/proxy/ttl_calculator.py (CVE=24h, exploit=1h, SPARQL=5min)
- [ ] T084 [US6] Implement HTTP proxy handler in src/services/proxy/proxy_handler.py with httpx.AsyncClient
- [ ] T085 [US6] Create proxy routes in src/api/proxy_routes.py (GET /proxy/{path:path})
- [ ] T086 [US6] Add X-Cache header to responses (HIT/MISS)
- [ ] T087 [US6] Implement cache invalidation on ingestion updates
- [ ] T088 [US6] Add cache hit rate metrics and logging
- [ ] T089 [US6] Implement graceful degradation when Redis unavailable

**Checkpoint**: All user stories complete - full system functional with caching optimization

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T090 [P] Create comprehensive README.md with setup, usage examples, architecture diagram
- [ ] T091 [P] Add --help documentation for all CLI subcommands
- [ ] T092 [P] Create example SPARQL queries in docs/examples/sparql_queries.md
- [ ] T093 [P] Create demo subscriber client in src/cli/demo_subscriber.py (receives webhooks)
- [ ] T094 [P] Add Prometheus metrics endpoint in src/api/metrics_routes.py (optional)
- [ ] T095 [P] Run black formatter on all Python files per constitution
- [ ] T096 [P] Run mypy type checking on all source files
- [ ] T097 [P] Add API documentation using FastAPI's automatic OpenAPI generation
- [ ] T098 [P] Create troubleshooting guide in docs/troubleshooting.md
- [ ] T099 Validate quickstart.md instructions by running from scratch
- [ ] T100 Run full test suite and verify 70%+ coverage per constitution
- [ ] T101 Security audit: validate input sanitization, rate limiting, query timeouts
- [ ] T102 Performance testing: verify success criteria (SC-001 through SC-010) are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Ingestion: No dependencies on other stories
  - User Story 2 (P2) - SPARQL: Depends on US1 data being available (but can develop in parallel with mock data)
  - User Story 3 (P3) - Pub/Sub: Depends on US1 ingestion triggering notifications
  - User Story 4 (P4) - WebSub: Builds on US3 pub/sub infrastructure
  - User Story 5 (P5) - Multi-format: Depends on US1 data and US2 SPARQL endpoint
  - User Story 6 (P6) - Caching: Can wrap any existing endpoints (minimal dependencies)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Ingestion)**: Independent - can complete fully without other stories
- **US2 (SPARQL)**: Independent - can complete with US1 data or test fixtures
- **US3 (Pub/Sub)**: Requires US1 ingestion to trigger notifications
- **US4 (WebSub)**: Extends US3 pub/sub with WebSub protocol
- **US5 (Multi-format)**: Requires US1 data; benefits from US2 SPARQL but not required
- **US6 (Caching)**: Independent - wraps existing endpoints

### Within Each User Story

- Tests FIRST → Models → Services → API Routes → Integration
- All [P] tasks within a phase can run in parallel
- Core implementation before cross-story integration

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006, T007, T008, T009 can all run in parallel
- **Phase 2 (Foundational)**: T011-T018 can all run in parallel after T010
- **Phase 3 (US1)**: T020-T022 tests in parallel; T024-T026 models in parallel
- **User Stories**: US1, US2, US6 can be developed in parallel by different developers
- **Phase 9 (Polish)**: Most tasks T090-T098 can run in parallel

---

## Parallel Example: User Story 1 (Ingestion)

```bash
# Launch all tests together:
Parallel batch 1:
- T020: Unit test for NVD client
- T021: Unit test for EUVD client
- T022: Unit test for RDF serializer

# Launch all models together:
Parallel batch 2:
- T024: Vulnerability model
- T025: SoftwareRef model
- T026: Advisory model

# Sequential after models complete:
- T027: NVD client (uses T024, T025)
- T028: EUVD client (uses T024, T025)
- T029: RDF serializer (uses T024, T025, T026)
# ... continue with remaining tasks
````

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T019) - **CRITICAL CHECKPOINT**
3. Complete Phase 3: User Story 1 - Ingestion (T020-T036)
4. **VALIDATE US1**: Ingest sample CVEs, verify RDF storage
5. Complete Phase 4: User Story 2 - SPARQL (T037-T046)
6. **VALIDATE US2**: Query ingested data via SPARQL endpoint
7. **DEMO READY**: MVP with ingestion + querying functional

### Incremental Delivery

1. MVP (US1 + US2) → Deploy/Demo
2. Add US3 (Pub/Sub) → Test independently → Deploy/Demo
3. Add US4 (WebSub) → Test independently → Deploy/Demo
4. Add US5 (Multi-format) → Test independently → Deploy/Demo
5. Add US6 (Caching) → Test independently → Deploy/Demo
6. Polish (Phase 9) → Final release

### Parallel Team Strategy

With 3 developers after Foundational phase complete:

- **Developer A**: US1 (Ingestion) + US3 (Pub/Sub)
- **Developer B**: US2 (SPARQL) + US5 (Multi-format)
- **Developer C**: US4 (WebSub) + US6 (Caching)

---

## Summary

- **Total Tasks**: 102
- **Setup Tasks**: 9 (Phase 1)
- **Foundational Tasks**: 10 (Phase 2)
- **User Story Tasks**: 70 (Phases 3-8)
  - US1 (Ingestion): 17 tasks
  - US2 (SPARQL): 10 tasks
  - US3 (Pub/Sub): 13 tasks
  - US4 (WebSub): 8 tasks
  - US5 (Multi-format): 10 tasks
  - US6 (Caching): 12 tasks
- **Polish Tasks**: 13 (Phase 9)
- **Parallelizable Tasks**: 45 marked with [P]
- **MVP Scope**: Phases 1, 2, 3, 4 (T001-T046) = 46 tasks

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] marker indicates tasks that can run in parallel (different files, no blocking dependencies)
- [Story] marker (US1-US6) maps tasks to user stories for traceability
- Each user story phase delivers independently testable functionality
- Tests included per constitution requirement (70% coverage minimum)
- Constitution compliance: structured logging, type hints, docstrings, PEP 8 enforced
- Stop at any checkpoint to validate story independently before proceeding
