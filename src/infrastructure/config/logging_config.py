"""
Centralized logging configuration for FireFlow application.

This module provides comprehensive logging setup using Python's standard logging library
with proper configuration based on application settings.
"""

import logging
import logging.handlers
import sys
from pathlib import Path

from flask import Flask

from .settings import LoggingSettings


class LoggingConfig:
    """Centralized logging configuration manager."""

    def __init__(self, settings: LoggingSettings):
        """Initialize logging configuration with settings."""
        self.settings = settings
        self._configured = False

    def configure_logging(self, app: Flask | None = None) -> None:
        """Configure logging for the application."""
        if self._configured:
            return

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.settings.level))

        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Configure formatters
        formatter = logging.Formatter(
            fmt=self.settings.format, datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler (always present)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.settings.level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (if specified)
        if self.settings.file_path:
            self._setup_file_handler(root_logger, formatter)

        # Configure specific loggers
        self._configure_third_party_loggers()

        # Configure Flask app logging if provided
        if app:
            self._configure_flask_logging(app)

        self._configured = True

        # Log configuration completion
        logger = logging.getLogger(__name__)
        logger.info(
            f"Logging configured - Level: {self.settings.level}, "
            f"File: {self.settings.file_path or 'Console only'}"
        )

    def _setup_file_handler(
        self, root_logger: logging.Logger, formatter: logging.Formatter
    ) -> None:
        """Set up rotating file handler for log files."""
        try:
            # Create log directory if it doesn't exist
            log_path = Path(self.settings.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.settings.file_path,
                maxBytes=self.settings.max_file_size_mb
                * 1024
                * 1024,  # Convert MB to bytes
                backupCount=self.settings.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(getattr(logging, self.settings.level))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        except OSError:
            # If file logging fails, log to console only
            console_logger = logging.getLogger(__name__)
            console_logger.exception(
                "Failed to setup file logging. Using console only."
            )

    def _configure_third_party_loggers(self) -> None:
        """Configure logging levels for third-party libraries."""
        # Set logging levels for noisy third-party libraries
        third_party_loggers = {
            "werkzeug": "WARNING",
            "urllib3": "WARNING",
            "requests": "WARNING",
            "celery": "INFO",
            "sqlalchemy.engine": "WARNING",
            "sqlalchemy.pool": "WARNING",
            "sqlalchemy.dialects": "WARNING",
            "alembic": "INFO",
            "redis": "WARNING",
        }

        for logger_name, level in third_party_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level))

    def _configure_flask_logging(self, app: Flask) -> None:
        """Configure Flask-specific logging."""
        # Configure Flask's logger
        app.logger.setLevel(getattr(logging, self.settings.level))

        # Remove Flask's default handler to avoid duplicate logs
        if app.logger.handlers:
            for handler in app.logger.handlers[:]:
                app.logger.removeHandler(handler)

        # Make Flask logger use our configured root logger
        app.logger.propagate = True


def setup_logging(settings: LoggingSettings, app: Flask | None = None) -> LoggingConfig:
    """
    Set up logging configuration for the application.

    Args:
        settings: LoggingSettings instance with configuration
        app: Optional Flask app instance

    Returns:
        LoggingConfig instance for further customization if needed
    """
    logging_config = LoggingConfig(settings)
    logging_config.configure_logging(app)
    return logging_config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    This is a convenience function that returns a standard logging.Logger
    configured with the application's logging settings.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured Logger instance
    """
    return logging.getLogger(name)
