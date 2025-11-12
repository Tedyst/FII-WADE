# Data Model

This document describes the RDF vocabulary, core entities, and Pydantic models used in the Vulnerability DDS project.

## Namespaces

- `vuln:` -> `http://wade.example.org/vuln#`
- `schema:` -> `https://schema.org/`
- `dcterms:` -> `http://purl.org/dc/terms/`

## RDF Classes

- `vuln:Vulnerability`
  - `vuln:cveId` (xsd:string)
  - `vuln:cvssScore` (xsd:float)
  - `vuln:publishedDate` (xsd:date)
  - `vuln:modifiedDate` (xsd:date)
  - `vuln:cvssVector` (xsd:string)
  - `vuln:affectsSoftware` -> link to `schema:SoftwareApplication` or `schema:SoftwareSourceCode`
  - `vuln:hasAdvisory` -> `vuln:Advisory`

- `vuln:Advisory`
  - `dcterms:identifier` (xsd:string)
  - `dcterms:title` (xsd:string)
  - `dcterms:description` (xsd:string)
  - `vuln:publishedBy` (xsd:string)
  - `vuln:advisoryUrl` (xsd:anyURI)

- `vuln:Exploit`
  - `vuln:exploitId`
  - `vuln:exploitUrl`
  - `vuln:exploitPublishedDate`

- `schema:SoftwareApplication` (use schema.org fields)
  - `schema:name`
  - `schema:applicationCategory` ("CMS", "WebFramework", "ShoppingCart")
  - `schema:softwareVersion`
  - `schema:codeRepository`

- `vuln:Subscription`
  - `vuln:subscriptionId` (UUID)
  - `vuln:topic` (string)
  - `vuln:callbackUrl` (URI)
  - `vuln:filters` (JSON literal)
  - `vuln:expiresAt` (xsd:dateTime)

## Pydantic Models (source code mapping)

### Vulnerability (pydantic)

- `cve_id: str`
- `description: str`
- `cvss_score: float | None`
- `cvss_vector: str | None`
- `published_date: date | None`
- `modified_date: date | None`
- `affected: list[SoftwareRef]`  # simplified mapping to software
- `references: list[str]`
- `raw: dict`  # original source JSON

### SoftwareRef

- `name: str`
- `vendor: str | None`
- `product: str | None`
- `version: str | None`
- `category: str | None`  # e.g., CMS, Framework

### Advisory

- `id: str`
- `title: str`
- `text: str`
- `url: str`
- `published_by: str`

### Subscription

- `id: UUID`
- `topic: str`
- `callback_url: Optional[str]`
- `filters: dict`
- `connection_type: Literal['webhook','sse','ws']`
- `created_at: datetime`
- `expires_at: Optional[datetime]`

## RDF Mapping Notes

- Convert Pydantic models to RDF triples using `pyoxigraph.Term` and `pyoxigraph.Quad` helpers.
- Each vulnerability is represented as a URI `http://wade.example.org/vuln/{cve-id}`.
- Software entities are represented as blank nodes or URIs when a repository or product identifier exists.
- Map `SoftwareRef` to `schema:SoftwareApplication` when enough metadata is present.

## Validation Rules

- `cve_id` must match regex `^CVE-\d{4}-\d+$` where possible.
- `cvss_score` between 0.0 and 10.0 when present.
- `subscription.callback_url` must be a valid `http` or `https` URL for webhooks.

## Example RDF (Turtle)

```turtle
@prefix vuln: <http://wade.example.org/vuln#> .
@prefix schema: <https://schema.org/> .

<http://wade.example.org/vuln/CVE-2024-1234> a vuln:Vulnerability ;
  vuln:cveId "CVE-2024-1234" ;
  vuln:cvssScore 9.8 ;
  vuln:publishedDate "2024-06-01"^^xsd:date ;
  vuln:affectsSoftware [ a schema:SoftwareApplication ; schema:name "ExampleCMS" ; schema:applicationCategory "CMS" ] .
```
