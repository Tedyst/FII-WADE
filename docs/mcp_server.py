#!/usr/bin/env python3
"""
Minimal MCP-style demo server exposing a single function `get_wade`.

POST /invoke  with JSON {"function": "get_wade", "args": []}
returns JSON {"result": "<html>...</html>"}

No external dependencies; uses stdlib HTTP server and urllib.
"""
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
WADE_URL = "https://profs.info.uaic.ro/sabin.buraga/teach/courses/wade/web-film.html"


def get_wade():
    """Fetch the WADE page and return its HTML as a string."""
    with urllib.request.urlopen(WADE_URL, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"status": "ok"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/invoke":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""

        try:
            req = json.loads(body.decode("utf-8"))
            func = req.get("function")
            args = req.get("args", [])

            if func == "get_wade":
                result = get_wade()
                self._send_json({"result": result})
            else:
                self._send_json({"error": f"unknown function {func}"}, code=400)

        except Exception as e:
            self._send_json({"error": str(e)}, code=500)


def run():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"MCP demo server listening on http://127.0.0.1:{PORT} (POST /invoke)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        server.server_close()


if __name__ == "__main__":
    run()
