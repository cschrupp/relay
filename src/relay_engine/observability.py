"""Structured logging configuration for Relay."""

from __future__ import annotations

import logging
import sys
from collections.abc import Sequence

import structlog

from relay_engine.settings import RelaySettings


def _shared_processors() -> list[structlog.types.Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def configure_logging(settings: RelaySettings) -> None:
    """Configure deterministic process logging from explicit settings.

    Calling this function repeatedly is safe: the root handler is replaced rather
    than accumulated, and structlog is reconfigured with the same explicit policy.
    """

    renderer: structlog.types.Processor
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=False)

    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(message)s",
        stream=sys.stdout,
        force=True,
    )

    processors: Sequence[structlog.types.Processor] = [
        *_shared_processors(),
        renderer,
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, settings.log_level)),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger."""

    return structlog.get_logger(name)
