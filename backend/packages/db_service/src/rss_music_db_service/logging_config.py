"""Structured logging config for the DB Service."""

import logging
import structlog
import sys
from collections import OrderedDict
from typing import Any


def order_keys(logger, name, event_dict):
    """Ensure consistent field ordering."""
    ordered = OrderedDict()
    for key in ["timestamp", "level", "event", "message", "route", "statusCode"]:
        if key in event_dict:
            ordered[key] = event_dict[key]
    for key, value in event_dict.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            order_keys,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)


def log_request(
    logger: structlog.BoundLogger,
    level: str,
    event: str,
    message: str,
    route: str = "",
    status_code: int = 200,
    **extra_fields: Any,
) -> None:
    """Log a request event w/ structured fields."""
    log_method = getattr(logger, level)
    log_method(
        event,
        message=message,
        route=route,
        statusCode=status_code,
        **extra_fields,
    )
