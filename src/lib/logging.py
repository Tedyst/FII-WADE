"""Structured logging configuration per constitution requirements.

All diagnostic output uses Python's standard logging library.
"""

import logging
import sys


def setup_logging(level: str = "INFO", format_json: bool = False) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_json: If True, output JSON format; otherwise human-readable

    Per constitution:
    - Use logging module exclusively (no print statements)
    - Structured format with timestamp, level, module, message
    - CLI output: INFO+ to stderr, results to stdout
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if format_json:
        # JSON format for production
        log_format = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"module":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Human-readable format for development
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,  # Per constitution: diagnostic to stderr
        force=True,
    )

    # Silence noisy third-party loggers
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
