"""
Centralized logging configuration for the application.
All modules should import logger from here instead of using print().
"""

import logging
import sys


def _build_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with a single StreamHandler.
    Call once at application startup (lifespan).
    """
    root = logging.getLogger()
    if root.handlers:
        return  # Already configured, avoid duplicate handlers

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    root.setLevel(level)
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
