"""Logging configuration."""
import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Setup application logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on LOG_FORMAT
    if settings.LOG_FORMAT.lower() == "json":
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            timestamp=True
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure Uvicorn access logger
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.setLevel(log_level)
    uvicorn_logger.handlers = [console_handler]


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context for adding structured logging context."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize log context."""
        self.context = kwargs

    def __enter__(self) -> "LogContext":
        """Enter context."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return self.context
