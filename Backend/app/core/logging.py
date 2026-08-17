"""
Centralized logging configuration for the application.
All modules should import logger from here instead of using print().
"""

import logging
import json
import sys
from datetime import datetime, timezone

from app.core.config import settings


def _build_formatter() -> logging.Formatter:
    if settings.LOG_FORMAT == "json":
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    payload["exception"] = self.formatException(record.exc_info)
                return json.dumps(payload, ensure_ascii=False)

        return JsonFormatter()
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def configure_logging(level: int | None = None) -> None:
    """
    Configure root logger with a single StreamHandler.
    Call once at application startup (lifespan).
    """
    root = logging.getLogger()
    if root.handlers:
        return  # Already configured, avoid duplicate handlers

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    configured_level = level or getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(configured_level)
    root.addHandler(handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger. Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
