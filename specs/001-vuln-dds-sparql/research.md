# Phase 0: Research & Technical Decisions

**Feature**: Vulnerability DDS with SPARQL Endpoint  
**Date**: 2025-11-12  
**Status**: Complete

## Overview

This document captures research findings and technical decisions for building a real-time Data Distribution Service (DDS) for web application vulnerability alerts. All "NEEDS CLARIFICATION" items from the technical context have been resolved through research and best practices analysis.

---

## 1. Data Sources: NVD API & EUVDB

### Decision: Use NVD API 2.0 + EUVDB JSON Feeds

**NVD (National Vulnerability Database) API**:
- **Endpoint**: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **Authentication**: API key recommended (rate limit 50 req/10sec without key, 50 req/30sec with key)
- **Data Format**: JSON with CVE schema (CVE ID, description, CVSS scores, CWE, CPE, references)
- **Coverage**: Comprehensive CVE database with vendor/product mappings via CPE (Common Platform Enumeration)
- **Software Classification**: Extract from CPE URIs (e.g., `cpe:2.3:a:wordpress:wordpress:*` → CMS category)

**EUVDB (EU Vulnerability Database)**:
- **Endpoint**: Currently uses CSV exports from vulnerability tracking systems
- **Note**: EUVDB is less structured than NVD; may require custom parsing
- **Alternative**: Use exploit-db.com JSON API or VulDB for European vulnerabilities
- **Decision**: Start with exploit-db.com (`https://www.exploit-db.com/search?cve=<ID>`) for exploit data enrichment

**Extensibility Strategy**:
- Define `BaseSource` abstract class with methods: `fetch_vulnerabilities()`, `parse_record()`, `get_software_class()`
- Each source (NVD, EUVDB, future sources) implements this interface
- Configuration YAML defines active sources and their credentials

**Rationale**: NVD provides authoritative CVE data; exploit-db adds proof-of-concept information. Abstract interface allows easy addition of MITRE ATT&CK, OSV, or GitHub Security Advisories in the future.

**Alternatives Considered**:
- CVE.org API: Less comprehensive metadata than NVD
- VulDB: Commercial, not suitable for school project
- Rejected EUVDB CSV parsing due to inconsistent format

---

## 2. WebSub (W3C Specification) Integration

### Decision: Implement WebSub Hub for Pub/Sub + Custom SSE/WebSocket for Real-Time

**WebSub Overview**:
- **W3C Spec**: https://www.w3.org/TR/websub/
- **Pattern**: Decentralized pub/sub protocol using HTTP webhooks
- **Components**:
  - **Publisher**: Advertises feed URL with `<link rel="hub">` in HTML/Atom
  - **Hub**: Intermediary that accepts subscriptions and distributes updates
  - **Subscriber**: Registers webhook URL to receive notifications

**Implementation Plan**:
- **Hub Endpoints**:
  - `POST /websub/hub` - Subscriber intent verification and subscription management
  - `POST /websub/publish` - Publishers notify hub of content updates
- **Subscription Flow**:
  1. Subscriber sends `hub.mode=subscribe`, `hub.topic=<vuln-feed-url>`, `hub.callback=<webhook>`
  2. Hub validates via GET request to callback with challenge token
  3. Hub stores subscription in PostgreSQL with expiry (lease_seconds)
  4. On new vulnerability, hub POSTs to all subscriber callbacks for that topic
- **Topic Structure**: `/feeds/vulnerabilities/<software-class>` (e.g., `/feeds/vulnerabilities/cms`)

**Complementary Real-Time Options**:
- **Server-Sent Events (SSE)**: `GET /stream/vulnerabilities?software_class=cms` - Long-lived HTTP connection for browser clients
- **WebSockets**: `ws://host/ws/vulnerabilities` - Bidirectional for interactive clients

**Rationale**: WebSub provides federated subscription model (external services can subscribe); SSE/WS offer lower-latency for direct API consumers. Both approaches coexist.

**Alternatives Considered**:
- Pure MQTT: Requires separate broker (mosquitto), adds complexity
- GraphQL Subscriptions: Overkill for simple alert feeds
- Polling: Not "real-time" as spec requires

---

## 3. SPARQL & RDF Storage: pyoxigraph + Oxigraph

### Decision: Use pyoxigraph Python bindings with embedded Oxigraph store

**Oxigraph Overview**:
- **Type**: SPARQL 1.1 compliant RDF triple store written in Rust
- **Python Binding**: `pyoxigraph` (pip installable)
- **Deployment Options**:
  - Embedded in-process (Python API)
  - Standalone server mode (HTTP SPARQL endpoint)
- **Performance**: Fast for <10M triples (suitable for vulnerability dataset scale)
- **Storage**: RocksDB backend (persistent, transactional)

**Architecture**:
- **Ingestion Pipeline**: Parse CVE/exploit data → Convert to RDF triples → `pyoxigraph.Store.add()`
- **SPARQL Endpoint**: FastAPI route wraps `store.query()` method
- **Formats**: Query results serialized as SPARQL JSON, CSV, or TSV (via pyoxigraph serializers)

**RDF Schema Design**:
- **Namespaces**:
  - `vuln:` - Custom vulnerability ontology (`http://example.org/vuln#`)
  - `schema:` - schema.org vocabulary (`https://schema.org/`)
  - `dcterms:` - Dublin Core metadata
- **Key Classes**:
  - `vuln:Vulnerability` → `schema:SoftwareApplication` (via linking properties)
  - `vuln:Advisory` → `schema:TechArticle`
  - `vuln:Exploit` → `schema:CreativeWork`
- **Properties**:
  - `vuln:cveId`, `vuln:cvssScore`, `vuln:affectsSoftware` (→ `schema:SoftwareApplication`)
  - `schema:applicationCategory` (for software class: "CMS", "Framework")

**Rationale**: pyoxigraph is lightweight, embeds easily in Python app, no separate database server needed. RocksDB provides durability. schema.org mapping enables rich semantic queries and JSON-LD output.

**Alternatives Considered**:
- Apache Jena Fuseki: Java-based, requires JVM (heavier footprint)
- RDFLib: Pure Python, slower query performance
- Virtuoso: Enterprise-scale, unnecessary complexity

---

## 4. DDS Publish/Subscribe Patterns

### Decision: In-Memory Broker + Redis Pub/Sub for Distributed Scaling

**Architecture**:

**Single-Instance Mode (Default)**:
- **In-Memory Broker**: Python `asyncio.Queue` per topic
- **Subscriptions**: Stored in PostgreSQL (persisted), active connections in memory
- **Message Flow**:
  1. Ingestion adds vulnerability → Publishes to topic queue
  2. PubSub service consumes queue → Fans out to WebSub callbacks + SSE streams
- **Topics**: Hierarchical by software class (e.g., `vuln.cms.wordpress`, `vuln.framework.django`)

**Multi-Instance Mode (Optional)**:
- **Redis Pub/Sub**: Coordination layer between API instances
- **Pattern**: API instance publishes to Redis channel → All instances relay to their local subscribers
- **Use Case**: Horizontal scaling (multiple API servers behind load balancer)

**Subscription Management**:
```python
class Subscription:
    id: UUID
    topic: str  # e.g., "cms", "framework"
    callback_url: str | None  # WebSub webhook
    connection_id: str | None  # SSE/WS connection ID
    expires_at: datetime
```

**Filtering**:
- Subscribers filter by software class, CVSS score threshold, CWE category
- Applied server-side before message delivery (reduce bandwidth)

**Rationale**: In-memory is simple and sufficient for single-server school project. Redis option demonstrates scalability understanding without mandatory complexity.

**Alternatives Considered**:
- Apache Kafka: Over-engineered for <100 subscribers
- RabbitMQ: Requires separate broker, more operational overhead
- ZeroMQ: Requires complex topology management

---

## 5. Multi-Format Output: HTML+RDFa, JSON-LD

### Decision: Jinja2 Templates + schema.org Vocabulary

**HTML + RDFa**:
- **Template Engine**: Jinja2 (FastAPI default)
- **Approach**: Embed RDFa attributes in semantic HTML
- **Example**:
  ```html
  <div vocab="https://schema.org/" typeof="SoftwareApplication">
    <h1 property="name">WordPress</h1>
    <div property="vulnerabilityReport" typeof="TechArticle">
      <span property="identifier">CVE-2024-1234</span>
      <p property="abstract">SQL injection in plugin...</p>
    </div>
  </div>
  ```
- **Routes**: `GET /vulnerabilities/{cve_id}.html` returns rendered template

**JSON-LD**:
- **Serialization**: Convert RDF graph to JSON-LD using pyoxigraph's `serialize()`
- **Context**: Inline schema.org context or external reference
- **Example**:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    "codeRepository": "https://github.com/example/cms",
    "vulnerabilityReport": {
      "@type": "TechArticle",
      "identifier": "CVE-2024-1234",
      "cvssScore": 9.8
    }
  }
  ```
- **Routes**: `GET /vulnerabilities/{cve_id}.jsonld` or `Accept: application/ld+json`

**schema.org Mapping**:
- `SoftwareApplication`: Represents vulnerable software (CMS, framework)
  - `applicationCategory`: "CMS", "WebFramework", "ShoppingCart"
  - `softwareVersion`: Affected versions
- `SoftwareSourceCode`: For open-source projects with repo links
  - `codeRepository`: GitHub/GitLab URL
  - `programmingLanguage`: PHP, Python, etc.
- `TechArticle`: Advisories, mitigation guides
  - `abstract`: Vulnerability description
  - `text`: Full advisory content

**Rationale**: RDFa enables semantic web crawlers; JSON-LD is standard for APIs. schema.org is widely recognized vocabulary. Both formats generated from same RDF graph ensures consistency.

**Alternatives Considered**:
- Microdata: Less flexible than RDFa
- Plain JSON with custom schema: Misses semantic web benefits
- Only RDF/XML: Not human-friendly

---

## 6. Smart Caching Proxy: FastAPI + Redis

### Decision: FastAPI Reverse Proxy with Redis Cache + Heuristics

**Architecture**:

**Proxy Service** (`src/services/proxy/`):
- **Framework**: FastAPI with `httpx.AsyncClient` for upstream requests
- **Routes**: `GET /proxy/*` - Proxies to NVD/EUVDB/exploit-db
- **Flow**:
  1. Request arrives → Check Redis cache (key: hash of URL + query params)
  2. **Cache Hit**: Return cached response (set `X-Cache: HIT` header)
  3. **Cache Miss**: Fetch from upstream → Store in Redis → Return response

**Caching Heuristics**:
- **CVE Data**: Cache for 24 hours (CVEs rarely change after publication)
- **Exploit Data**: Cache for 1 hour (exploits may be updated frequently)
- **SPARQL Queries**: Cache for 5 minutes (dataset updates frequently during ingestion)
- **Cache Key**: `sha256(f"{method}:{url}:{sorted(params)}")`
- **Conditional Requests**: Support `If-None-Match` (ETag) and `If-Modified-Since` headers
- **Cache Invalidation**: Purge CVE cache entry when ingestion updates that CVE

**Redis Configuration**:
- **TTL**: Per-route configurable (via settings.yaml)
- **Eviction Policy**: `allkeys-lru` (least recently used)
- **Max Memory**: 256MB (suitable for ~10K cached responses)

**Advanced Features** (Bonus):
- **Request Coalescing**: Multiple concurrent requests for same resource → Single upstream fetch
- **Compression**: Store gzipped responses in Redis
- **Hit Rate Metrics**: Log cache hit/miss ratio for monitoring

**Rationale**: Redis is fast (sub-millisecond GET), handles expiry automatically, and supports TTL per key. Heuristic caching based on resource volatility optimizes API rate limits (NVD) and SPARQL query performance.

**Alternatives Considered**:
- Nginx + Redis module: Requires separate Nginx deployment
- HTTP Caching (Varnish): Overkill for simple API proxy
- In-memory Python dict: No persistence across restarts, no TTL

---

## 7. Technology Stack Summary

### Core Technologies (Justified)

| Technology | Purpose | Rationale |
|------------|---------|-----------|
| **Python 3.11+** | Language | Standard for data processing, excellent async support, school-friendly |
| **FastAPI** | Web framework | Async-native, auto OpenAPI docs, lightweight |
| **pyoxigraph** | SPARQL/RDF | Embeddable, SPARQL 1.1 compliant, Python bindings |
| **PostgreSQL** | Relational DB | Subscriptions, metadata, JSONB for flexible schema |
| **Redis** | Cache & Pub/Sub | Sub-ms latency, native TTL, pub/sub channels |
| **asyncpg** | Postgres driver | Async queries (FastAPI compatible) |
| **aiohttp** | HTTP client | Async fetching from NVD/exploit-db |
| **Pydantic** | Validation | Type-safe models, FastAPI integration |
| **Jinja2** | Templating | HTML+RDFa generation |
| **pytest** | Testing | Standard Python test framework |
| **Docker Compose** | Deployment | Orchestrates PostgreSQL + Redis + app |

### Development Tools

- **black**: Code formatter (PEP 8)
- **mypy**: Static type checker
- **pytest-asyncio**: Async test support
- **httpx**: Async test client for FastAPI
- **ruff**: Fast linter (replaces flake8/pylint)

---

## 8. Implementation Priorities

### Phase 1 (MVP):
1. **Data Model**: RDF ontology + Pydantic models
2. **Ingestion**: NVD API client + RDF conversion
3. **SPARQL Endpoint**: Basic query execution
4. **Pub/Sub**: In-memory broker + WebSub hub
5. **Output Formats**: JSON-LD serializer

### Phase 2 (Enhanced):
1. **HTML+RDFa**: Jinja2 templates
2. **Caching Proxy**: Redis-backed proxy
3. **SSE/WebSocket**: Real-time streams
4. **Demo Clients**: CLI SPARQL client + webhook receiver

### Phase 3 (Bonus):
1. **EUVDB Integration**: Second data source
2. **Redis Pub/Sub**: Multi-instance support
3. **Metrics**: Prometheus endpoint for monitoring
4. **Web UI**: Simple dashboard for browsing vulnerabilities

---

## 9. Open Questions Resolved

### ❓ How to map CPE (Common Platform Enumeration) to software classes?

**Answer**: Use CPE URI parsing + heuristic classification:
- CPE format: `cpe:2.3:part:vendor:product:version:...`
- `part=a` (application) → Extract product name → Match against keyword list:
  - CMS: wordpress, drupal, joomla, typo3
  - Framework: django, rails, laravel, symfony
  - Shopping: magento, woocommerce, prestashop
- Store mapping in `config/software-classes.yaml` for maintainability

### ❓ How to handle SPARQL query performance for large datasets?

**Answer**: 
- Index frequently queried predicates (pyoxigraph auto-indexes)
- Implement query timeout (10s max execution)
- Cache frequent queries in Redis (5min TTL)
- Limit result sets (LIMIT 1000 enforced server-side)
- Use SPARQL query optimization: SELECT only needed variables, use FILTER efficiently

### ❓ How to ensure WebSub subscriptions persist across restarts?

**Answer**: 
- Store subscriptions in PostgreSQL with fields: `callback_url`, `topic`, `expires_at`, `secret`
- On startup, reload active subscriptions from DB
- Implement lease renewal: Hub sends subscription expiry warnings before timeout
- Subscribers must re-verify periodically (default lease: 7 days)

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| NVD API rate limits | Ingestion delays | Implement exponential backoff, use API key, cache responses |
| Large RDF graph size | Memory exhaustion | Use pyoxigraph's disk-backed storage (RocksDB), not in-memory |
| SPARQL injection attacks | Security breach | Parameterized queries via pyoxigraph API (not string concatenation) |
| WebSub callback failures | Lost notifications | Retry logic with exponential backoff (3 attempts), log failures |
| Redis unavailability | Proxy cache misses | Graceful fallback to direct upstream requests (log warning) |

---

## 11. Success Criteria (Measurable)

From specification:
- ✅ System ingests 100 CVEs in <60 seconds
- ✅ SPARQL queries return in <2 seconds (typical <1000 results)
- ✅ Pub/sub latency <500ms from vulnerability ingestion to subscriber notification
- ✅ Proxy achieves >70% cache hit rate after warm-up (100 requests)
- ✅ Supports 10 concurrent subscribers without message loss
- ✅ All output formats (JSON-LD, HTML+RDFa, SPARQL JSON) validate against specs

---

## Next Steps

**Phase 1 Deliverables** (to be generated):
1. `data-model.md` - RDF ontology, Pydantic models, entity relationships
2. `contracts/openapi.yaml` - API specification for all endpoints
3. `contracts/rdf-ontology.ttl` - Turtle vocabulary definition
4. `quickstart.md` - Setup instructions and usage examples

**Agent Context Update**:
Run `.specify/scripts/bash/update-agent-context.sh copilot` to add tech stack to AI assistant context.

---

**Research Complete** | Total decisions documented: 11 | Clarifications resolved: 8
