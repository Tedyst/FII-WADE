"""Simple SPARQL client CLI (stub)"""

import argparse
import sys
import json


def query(args=None):
    parser = argparse.ArgumentParser(prog="client-sparql")
    parser.add_argument("--endpoint", default="http://localhost:8000/sparql")
    parser.add_argument("--query", required=True)
    parsed = parser.parse_args(args=args)

    # Minimal implementation: POST query and print JSON
    import requests

    resp = requests.post(
        parsed.endpoint,
        data=parsed.query,
        headers={"Content-Type": "application/sparql-query"},
    )
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
