<!--
Sync Impact Report:
- Version change: N/A (initial) → 1.0.0
- Principles defined: Simplicity First, Structured Logging, Test Coverage, Modular Design, User Experience Consistency
- Added sections: Code Quality Standards, Performance Requirements
- Templates requiring updates: All templates are compatible (no conflicts with initial version)
- Follow-up TODOs: None
-->

# WADE Vulnerability DDS Constitution

## Core Principles

### I. Simplicity First (NON-NEGOTIABLE)

**This is a school project - prioritize clarity over cleverness**

- Code MUST be readable and understandable by fellow students
- Avoid overengineering: Use standard library solutions before external dependencies
- YAGNI principle: Implement only what the specification requires
- Direct, straightforward implementations preferred over abstract patterns
- Maximum function length: 50 lines (excluding docstrings)
- Maximum file length: 300 lines
- If complexity is unavoidable, document with inline comments explaining "why"

### II. Structured Logging (MANDATORY)

**All diagnostic output uses Python's standard logging library**

- Use `logging` module exclusively (no print statements in production code)
- Log levels MUST be appropriate:
  - DEBUG: Detailed diagnostics for development
  - INFO: Key operation milestones (e.g., "Started ingestion from NVD")
  - WARNING: Recoverable issues (e.g., "Failed to fetch CVE-2024-1234, retrying")
  - ERROR: Operation failures (e.g., "Database connection lost")
  - CRITICAL: System-level failures requiring intervention
- Structured format: Include timestamp, level, module, message
- CLI output: INFO+ to stderr, results to stdout (enables piping)
- Sensitive data MUST NOT appear in logs (API keys, credentials)

### III. Test Coverage (REQUIRED)

**Every module MUST have corresponding tests**

- Minimum 70% code coverage for non-trivial modules
- Test structure mirrors source structure: `tests/unit/test_<module>.py`
- Each public function/class requires at least one test case
- Integration tests MUST cover:
  - Data ingestion end-to-end (mock external APIs)
  - Pub/sub message flow
  - SPARQL query execution
  - Proxy caching behavior
- Tests run via `pytest` with clear naming: `test_<behavior>_<condition>_<expected>`
- Mock external dependencies (NVD API, EUVDB) to ensure reproducibility

### IV. Modular Design

**Components are independently testable and loosely coupled**

- Each service (ingestion, pubsub, SPARQL, proxy) operates through well-defined interfaces
- Configuration via YAML files (not hardcoded values)
- Database access isolated to `lib/db.py` module
- Data sources implement common `BaseSource` interface for extensibility
- RDF serialization separated from business logic
- CLI commands delegate to service modules (no business logic in CLI code)

### V. User Experience Consistency

**All interfaces follow predictable patterns**

- CLI commands use consistent verb-noun structure: `ingest nvd`, `query sparql`, `run api-server`
- Error messages MUST be actionable: State what failed + suggest remedy
- API responses follow standard HTTP status codes and JSON structure
- Documentation examples MUST be copy-pasteable and working
- SPARQL endpoint returns standard SPARQL JSON results format
- HTML output includes user-friendly rendering (not raw RDF dumps)

## Code Quality Standards

### Style and Formatting

- Follow PEP 8 conventions (enforced via `black` formatter if available)
- Type hints required for all function signatures
- Docstrings required for all public functions/classes (Google style)
- Import order: stdlib → third-party → local (grouped with blank lines)

### Error Handling

- Use specific exception types (avoid bare `except:`)
- Provide context in exceptions: `raise ValueError(f"Invalid CVE ID: {cve_id}")`
- Resource cleanup via context managers (`with` statements)
- Graceful degradation: Log errors and continue when possible (e.g., skip one CVE, process others)

### Security

- Input validation for all external data (CVE IDs, SPARQL queries, URLs)
- Sanitize user input before logging (prevent log injection)
- Rate limiting on ingestion APIs to respect NVD/EUVDB terms
- SPARQL query timeout limits (prevent DoS via expensive queries)

## Performance Requirements

**Suitable for academic demonstration with realistic constraints**

- SPARQL queries MUST respond in <2 seconds for typical queries (<1000 results)
- Pub/sub message delivery latency <500ms under normal load
- Proxy cache MUST improve response times by 50%+ for repeated requests
- System MUST handle 10 concurrent subscribers without degradation
- Ingestion MUST process 100 vulnerabilities in <60 seconds
- Memory usage MUST stay under 512MB during normal operation

## Development Workflow

### Code Review Checklist

Before considering code complete, verify:

- [ ] All tests pass (`pytest -v`)
- [ ] Logging uses `logging` module (no print statements)
- [ ] Functions have type hints and docstrings
- [ ] Complex logic includes explanatory comments
- [ ] Configuration is externalized (no hardcoded URLs/credentials)
- [ ] Error messages are helpful and actionable
- [ ] Code follows simplicity principle (no unnecessary abstractions)

### Documentation Requirements

- README MUST include: setup instructions, example commands, troubleshooting
- Each CLI command MUST have `--help` text explaining arguments
- API endpoints MUST be documented in OpenAPI spec
- RDF ontology MUST include comments explaining predicates

## Governance

**Constitution governs all development decisions for this project**

- All code reviews MUST verify compliance with these principles
- Violations require documented justification (added to plan.md Complexity Tracking)
- Constitution amendments require version bump and impact analysis
- For educational purposes: Prefer learning opportunities over perfect optimization

**Version**: 1.0.0 | **Ratified**: 2025-11-12 | **Last Amended**: 2025-11-12
