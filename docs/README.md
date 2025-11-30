# MCP demo (presentation)

Files added in `presentation/`:

- `index.html` — Reveal.js slides about MCP and MCP-B
- `mcp_server.py` — minimal MCP-style demo server exposing `get_wade`

Quick start

1. Run the demo server:

```bash
python3 presentation/mcp_server.py
```

2. Invoke the exported function `get_wade` (example using curl):

```bash
curl -s -X POST http://localhost:8765/invoke \
  -H 'Content-Type: application/json' \
  -d '{"function":"get_wade","args":[]}' > wade_result.json

# Then inspect the HTML inside wade_result.json
```

Notes

- The server listens on `127.0.0.1:8765` and supports `GET /health`.
- No external Python packages required; uses `urllib` from the stdlib.
- If you want a richer MCP protocol (typing, metadata, streaming), we can extend this.
