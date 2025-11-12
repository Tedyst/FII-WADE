# Quickstart

This quickstart runs the Vulnerability DDS locally using Docker Compose.

Prerequisites:

- Docker & Docker Compose
- Python 3.11+
- (Optional) `uv` package manager as requested; a `requirements.txt` is provided if `uv` is not available.

Steps:

1. Build and start services:

```bash
cd /home/tedy/Git/FII-WADE
docker compose -f docker/docker-compose.yml up --build
```

2. Install Python dependencies (if running locally):

```bash
# using pip
python -m pip install -r requirements.txt

# or using uv if available (user requested 'uv' package manager)
uv install
```

3. Run the API server (inside container or locally):

```bash
# from project root
python -m src.main api-server
```

4. Example: Run ingestion from EUVD (uses public EUVD API)

```bash
python -m src.main ingest-euvd
```

5. Query SPARQL endpoint

```bash
python -m src.main client-sparql --query 'SELECT ?s WHERE { ?s ?p ?o } LIMIT 10'
```

Notes:
- Web UI for RabbitMQ management is available at `http://localhost:15672` (guest/guest)
- Oxigraph HTTP UI available at `http://localhost:7878`
- PostgreSQL on `localhost:5432` (user: postgres, pass: postgres)

