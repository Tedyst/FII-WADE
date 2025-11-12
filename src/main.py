#!/usr/bin/env python3
"""Entry point for WADE Vulnerability DDS project.

Usage: python -m src.main api-server | ingest-nvd | ingest-euvd | client-sparql | run-proxy
"""

import argparse
import sys

from importlib import import_module


def run_api_server(args: argparse.Namespace) -> None:
    """Run the FastAPI server.

    Args:
        args: Command-line arguments
    """
    import uvicorn

    from lib.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "api.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=getattr(args, "reload", False),
        log_level=settings.log_level.lower(),
    )


def run_ingest_nvd(args):
    from cli.ingest import ingest_nvd

    ingest_nvd(args)


def run_ingest_euvd(args):
    from cli.ingest import ingest_euvd

    ingest_euvd(args)


def run_client_sparql(args):
    from cli.client_sparql import query

    query(args)


def run_proxy(args):
    from api.proxy import run as run_proxy

    run_proxy(args)


def main():
    parser = argparse.ArgumentParser(prog="wade")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("api-server", help="Run the FastAPI server")
    sub.add_parser("ingest-nvd", help="Run ingestion from NVD API")
    sub.add_parser("ingest-euvd", help="Run ingestion from EUVD API")
    sub.add_parser("client-sparql", help="Run a SPARQL client query")
    sub.add_parser("run-proxy", help="Run HTTP proxy")

    args = parser.parse_args()

    if args.cmd == "api-server":
        run_api_server(args)
    elif args.cmd == "ingest-nvd":
        run_ingest_nvd(args)
    elif args.cmd == "ingest-euvd":
        run_ingest_euvd(args)
    elif args.cmd == "client-sparql":
        run_client_sparql(args)
    elif args.cmd == "run-proxy":
        run_proxy(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
