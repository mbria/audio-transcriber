"""Structured logging setup with correlation IDs."""

import logging
import sys
from typing import Any

import structlog

from .config import get_correlation_id


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging with correlation IDs."""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_correlation_id,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def add_correlation_id(logger: Any, method_name: str, event_dict: Any) -> Any:
    """Add correlation ID to log events."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

