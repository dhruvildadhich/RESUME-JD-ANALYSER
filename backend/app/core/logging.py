"""
Structured JSON logging configuration.
Call setup_logging() once at application startup.
"""
import logging
import sys
from typing import Optional

try:
    from pythonjsonlogger.json import JsonFormatter as _JsonFormatter  # v3+
except ImportError:
    from pythonjsonlogger import jsonlogger as _json_module  # v2 fallback
    _JsonFormatter = _json_module.JsonFormatter  # type: ignore


def setup_logging(log_level: Optional[str] = "INFO") -> None:
    """Configure root logger to emit JSON-formatted log records."""
    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = _JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger; ensure it propagates to the root handler."""
    return logging.getLogger(name)
