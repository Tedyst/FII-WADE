# Feature Specification: Vulnerability DDS with SPARQL Endpoint

**Feature Branch**: `001-vuln-dds-sparql`  
**Created**: 2025-11-12  
**Status**: Draft  
**Input**: User description: "Using Web Application Exploits or a similar public dataset regarding the exploits on Web application vulnerabilities, build a smart DDS (Data Distribution Service) publish/subscribe system able to offer real-time alerts about new security issues for a specific class of software like CMS, frameworks, modules, shopping cart managers, etc. Also, study WebSub (W3C Specification). Additionally, the system will provide – via a SPARQL endpoint – various solutions (advice, technical reports, defensive programming guidelines and others) to prevent and/or eradicate such security incidents. This information will be available in multiple formats: HTML + RDFa, JSON-LD using Software Application and/or SoftwareSourceCode schema.org concepts. Bonus: including a smart Web proxy able to efficiently cache requested data."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Data Ingestion from Vulnerability Sources (Priority: P1)

Security researchers and system administrators need vulnerability data from NVD and EUVD APIs to be automatically ingested and stored in a queryable RDF format.

**Why this priority**: Without vulnerability data, the entire system has no value. This is the foundation for all other features.

**Independent Test**: Can be fully tested by running the ingestion CLI command and verifying that CVE records from NVD API and EUVD API are successfully stored in the pyoxigraph RDF store and can be retrieved via basic SPARQL queries.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** administrator runs `python -m src.main ingest-nvd`, **Then** latest CVEs from NVD API are fetched, converted to RDF triples, and stored in the graph
2. **Given** the system is running, **When** administrator runs `python -m src.main ingest-euvd`, **Then** latest vulnerabilities from EUVD API are fetched, converted to RDF triples with schema.org mapping, and stored
3. **Given** vulnerabilities are ingested, **When** a SPARQL query is executed for a specific CVE ID, **Then** the complete vulnerability record with affected software and CVSS score is returned

---

### User Story 2 - SPARQL Query Endpoint (Priority: P2)

Security analysts need to query vulnerability data using SPARQL to find specific vulnerabilities, affected software, advisories, and mitigation strategies.

**Why this priority**: This enables programmatic access to vulnerability intelligence and supports integration with security tools.

**Independent Test**: Can be fully tested by starting the API server and executing SPARQL queries via HTTP POST to `/sparql` endpoint, verifying results are returned in SPARQL JSON format with correct schema.org vocabulary mappings.

**Acceptance Scenarios**:

1. **Given** vulnerability data is ingested, **When** analyst sends SPARQL query "SELECT ?vuln WHERE { ?vuln a vuln:Vulnerability }", **Then** API returns list of all vulnerability URIs in SPARQL JSON format
2. **Given** vulnerability data exists, **When** analyst queries for CMS vulnerabilities with CVSS > 7.0, **Then** API returns filtered results with software metadata
3. **Given** a SPARQL query execution time exceeds 10 seconds, **When** the query is still running, **Then** the system terminates the query and returns a timeout error

---

### User Story 3 - Real-Time Pub/Sub Alerts (Priority: P3)

Development teams need to receive real-time notifications when new vulnerabilities affecting their specific software stack (CMS, frameworks, shopping carts) are discovered.

**Why this priority**: Real-time alerting enables proactive security response, reducing the window of exposure to newly discovered vulnerabilities.

**Independent Test**: Can be fully tested by subscribing to a topic (e.g., "cms"), ingesting a new CMS vulnerability, and verifying that the subscriber receives a notification via webhook callback or SSE stream within 500ms.

**Acceptance Scenarios**:

1. **Given** a subscriber registers with callback URL and topic "cms", **When** a new WordPress vulnerability is ingested, **Then** the subscriber's webhook receives a POST request with the vulnerability details
2. **Given** a subscriber connects via Server-Sent Events to `/stream/vulnerabilities?software_class=framework`, **When** a new Django vulnerability is ingested, **Then** the subscriber receives an SSE event with the vulnerability data
3. **Given** multiple subscribers are registered for different topics, **When** a new vulnerability is ingested, **Then** only subscribers whose topic matches the software class receive notifications

---

### User Story 4 - WebSub Hub Implementation (Priority: P4)

External security monitoring services need to subscribe to vulnerability feeds using the W3C WebSub protocol for federated pub/sub.

**Why this priority**: WebSub enables decentralized subscription model, allowing external systems to integrate without custom API clients.

**Independent Test**: Can be fully tested by implementing WebSub hub endpoints, performing subscription verification handshake, and confirming that external webhook callbacks receive notifications when content is published.

**Acceptance Scenarios**:

1. **Given** an external service sends WebSub subscription request with hub.mode=subscribe and hub.callback URL, **When** the hub validates the callback, **Then** the subscription is confirmed and stored
2. **Given** an active WebSub subscription exists, **When** new vulnerability content is published to the topic, **Then** the hub POSTs the update to the subscriber's callback URL
3. **Given** a subscription has expired (lease_seconds elapsed), **When** new content is published, **Then** the expired subscription does not receive notifications

---

### User Story 5 - Multi-Format Output (HTML+RDFa, JSON-LD) (Priority: P5)

Security portals and web applications need to display vulnerability information in human-readable HTML with embedded RDFa semantic annotations and JSON-LD for programmatic access.

**Why this priority**: Multiple output formats enable both human consumption (web browsers) and machine processing (semantic web tools, search engines).

**Independent Test**: Can be fully tested by requesting a vulnerability by CVE ID with different Accept headers and verifying: (1) HTML+RDFa response includes schema.org vocabulary attributes, (2) JSON-LD response validates against schema.org SoftwareApplication/SoftwareSourceCode schemas.

**Acceptance Scenarios**:

1. **Given** a vulnerability CVE-2024-1234 exists, **When** user requests GET `/vulnerabilities/CVE-2024-1234` with Accept: text/html, **Then** server returns HTML page with embedded RDFa annotations using schema.org vocabulary
2. **Given** a vulnerability exists, **When** user requests GET `/vulnerabilities/CVE-2024-1234` with Accept: application/ld+json, **Then** server returns JSON-LD with @context pointing to schema.org
3. **Given** vulnerability data with advisory links, **When** HTML+RDFa is rendered, **Then** the page includes clickable links to advisories marked up with schema:TechArticle

---

### User Story 6 - Smart Caching Proxy (Priority: P6)

System operators need efficient caching of upstream API requests (NVD, EUVD) and SPARQL query results to reduce latency and API rate limit consumption.

**Why this priority**: Caching improves performance, reduces external API load, and enables the system to handle higher query volumes.

**Independent Test**: Can be fully tested by making identical requests to proxied endpoints and verifying: (1) first request fetches from upstream, (2) subsequent requests return cached response with X-Cache: HIT header, (3) cache hit rate exceeds 70% after warm-up.

**Acceptance Scenarios**:

1. **Given** no cached data exists, **When** user requests `/proxy/nvd/cves/CVE-2024-1234`, **Then** proxy fetches from NVD API, caches response with 24-hour TTL, and returns data with X-Cache: MISS header
2. **Given** cached CVE data exists, **When** user requests the same CVE within TTL period, **Then** proxy returns cached response with X-Cache: HIT header in <50ms
3. **Given** SPARQL query cache exists, **When** identical query is executed within 5-minute TTL, **Then** cached results are returned without re-executing query

---

### Edge Cases

- What happens when NVD API rate limit is exceeded during ingestion? System should implement exponential backoff and retry logic, logging rate limit errors.
- How does system handle malformed SPARQL queries? System should validate queries, return 400 Bad Request with descriptive error message, and log the invalid query.
- What happens when a WebSub callback URL is unreachable? System should retry notification delivery up to 3 times with exponential backoff, then log delivery failure and continue processing other subscribers.
- How does system handle duplicate vulnerability ingestion? System should detect duplicate CVE IDs using RDF graph queries and update existing records rather than creating duplicates.
- What happens when Redis cache is unavailable? Proxy should gracefully degrade to direct upstream requests and log cache unavailability warnings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST fetch vulnerability data from NVD API 2.0 using API key authentication
- **FR-002**: System MUST fetch vulnerability data from EUVD API endpoints (/lastvulnerabilities, /criticalvulnerabilities, /search)
- **FR-003**: System MUST convert CVE/EUVD records to RDF triples using custom vuln: namespace and schema.org vocabulary
- **FR-004**: System MUST store RDF triples in pyoxigraph embedded store with persistent RocksDB backend
- **FR-005**: System MUST expose SPARQL 1.1 compliant query endpoint at `/sparql` accepting POST requests
- **FR-006**: System MUST classify vulnerabilities by software category (CMS, Framework, ShoppingCart, Module) based on CPE strings
- **FR-007**: System MUST implement pub/sub broker using RabbitMQ for multi-instance scalability
- **FR-008**: System MUST support WebSub hub protocol for subscription verification and content distribution
- **FR-009**: System MUST support Server-Sent Events (SSE) for real-time vulnerability streaming
- **FR-010**: System MUST generate HTML+RDFa output with schema:SoftwareApplication and schema:TechArticle markup
- **FR-011**: System MUST generate JSON-LD output with schema.org @context
- **FR-012**: System MUST implement HTTP caching proxy using Redis with configurable TTL per resource type
- **FR-013**: System MUST use Celery for asynchronous ingestion tasks with RabbitMQ as broker
- **FR-014**: System MUST validate all SPARQL queries and enforce 10-second execution timeout
- **FR-015**: System MUST log all operations using Python logging module with structured format
- **FR-016**: CLI MUST provide subcommands: api-server, ingest-nvd, ingest-euvd, client-sparql, run-proxy
- **FR-017**: System MUST persist subscriptions in PostgreSQL with fields: callback_url, topic, filters, expires_at
- **FR-018**: System MUST support subscription filtering by software class, CVSS score range, and CWE category

### Key Entities

- **Vulnerability**: Represents a CVE/EUVD record with ID, description, CVSS score, publication date, affected software references
- **SoftwareRef**: Represents affected software with name, vendor, product, version, category (CMS/Framework/etc.)
- **Advisory**: Represents mitigation guidance with ID, title, description, URL, publisher
- **Subscription**: Represents pub/sub subscription with ID, topic, callback URL, filters, expiration
- **Exploit**: Represents known exploit with ID, URL, publication date, linked vulnerability

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System ingests 100 CVE records from NVD API in under 60 seconds
- **SC-002**: SPARQL queries returning up to 1000 results complete in under 2 seconds (p95 latency)
- **SC-003**: Pub/sub notification delivery latency is under 500ms from ingestion to subscriber callback
- **SC-004**: Caching proxy achieves >70% cache hit rate after processing 100 requests
- **SC-005**: System handles 10 concurrent subscribers without message loss or latency degradation
- **SC-006**: HTML+RDFa output validates against W3C RDFa validator
- **SC-007**: JSON-LD output validates against schema.org SoftwareApplication schema
- **SC-008**: WebSub subscription verification handshake completes successfully within 5 seconds
- **SC-009**: System memory usage remains under 512MB during normal operation (10 concurrent queries, 50 subscribers)
- **SC-010**: All CLI commands provide helpful --help documentation and return meaningful error messages
