"""RDF namespace definitions for WADE Vulnerability DDS.

Per research.md: vuln:, schema:, dcterms: namespaces
"""

from pyoxigraph import NamedNode

# Custom vulnerability namespace
VULN = "http://wade.example.org/vuln#"

# schema.org vocabulary
SCHEMA = "https://schema.org/"

# Dublin Core Terms
DCTERMS = "http://purl.org/dc/terms/"

# RDF/RDFS/OWL
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"


class VULN_NS:
    """Vulnerability namespace predicates."""

    Vulnerability = NamedNode(f"{VULN}Vulnerability")
    Advisory = NamedNode(f"{VULN}Advisory")
    Exploit = NamedNode(f"{VULN}Exploit")

    cveId = NamedNode(f"{VULN}cveId")
    cvssScore = NamedNode(f"{VULN}cvssScore")
    cvssVector = NamedNode(f"{VULN}cvssVector")
    publishedDate = NamedNode(f"{VULN}publishedDate")
    modifiedDate = NamedNode(f"{VULN}modifiedDate")
    affectsSoftware = NamedNode(f"{VULN}affectsSoftware")
    hasAdvisory = NamedNode(f"{VULN}hasAdvisory")
    hasExploit = NamedNode(f"{VULN}hasExploit")


class SCHEMA_NS:
    """schema.org vocabulary predicates."""

    SoftwareApplication = NamedNode(f"{SCHEMA}SoftwareApplication")
    SoftwareSourceCode = NamedNode(f"{SCHEMA}SoftwareSourceCode")
    TechArticle = NamedNode(f"{SCHEMA}TechArticle")
    CreativeWork = NamedNode(f"{SCHEMA}CreativeWork")

    name = NamedNode(f"{SCHEMA}name")
    applicationCategory = NamedNode(f"{SCHEMA}applicationCategory")
    softwareVersion = NamedNode(f"{SCHEMA}softwareVersion")
    codeRepository = NamedNode(f"{SCHEMA}codeRepository")
    programmingLanguage = NamedNode(f"{SCHEMA}programmingLanguage")
    vulnerabilityReport = NamedNode(f"{SCHEMA}vulnerabilityReport")
    identifier = NamedNode(f"{SCHEMA}identifier")
    abstract = NamedNode(f"{SCHEMA}abstract")
    text = NamedNode(f"{SCHEMA}text")


class DCTERMS_NS:
    """Dublin Core Terms predicates."""

    identifier = NamedNode(f"{DCTERMS}identifier")
    title = NamedNode(f"{DCTERMS}title")
    description = NamedNode(f"{DCTERMS}description")
    created = NamedNode(f"{DCTERMS}created")
    modified = NamedNode(f"{DCTERMS}modified")
    publisher = NamedNode(f"{DCTERMS}publisher")


class RDF_NS:
    """RDF vocabulary."""

    type = NamedNode(f"{RDF}type")
