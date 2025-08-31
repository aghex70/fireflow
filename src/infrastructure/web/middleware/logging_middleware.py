"""Request/Response logging middleware for Flask application."""

import time
import uuid
from typing import Any

import structlog
from flask import Flask, g, request
from werkzeug.local import LocalProxy


logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app: Flask | None = None):
        """Initialize logging middleware."""
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize logging middleware for Flask app."""
        self.app = app
        self._register_middleware()

    def _register_middleware(self):
        """Register before and after request handlers."""

        @self.app.before_request
        def before_request():
            """Log request details and set up request context."""
            # Generate unique request ID
            g.request_id = str(uuid.uuid4())[:8]
            g.start_time = time.time()

            # Skip logging for health checks and static files
            if self._should_skip_logging():
                return

            # Extract request details
            request_data = self._extract_request_data()

            logger.info(
                "Incoming request",
                request_id=g.request_id,
                **request_data,
            )

        @self.app.after_request
        def after_request(response):
            """Log response details."""
            # Skip logging for health checks and static files
            if self._should_skip_logging():
                return response

            # Calculate request duration
            duration = time.time() - getattr(g, "start_time", time.time())

            # Extract response details
            response_data = self._extract_response_data(response, duration)

            # Log based on status code
            if response.status_code >= 500:
                logger.exception(
                    "Request completed with server error",
                    request_id=getattr(g, "request_id", "unknown"),
                    **response_data,
                )
            elif response.status_code >= 400:
                logger.warning(
                    "Request completed with client error",
                    request_id=getattr(g, "request_id", "unknown"),
                    **response_data,
                )
            else:
                logger.info(
                    "Request completed successfully",
                    request_id=getattr(g, "request_id", "unknown"),
                    **response_data,
                )

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = getattr(g, "request_id", "unknown")

            return response

    def _should_skip_logging(self) -> bool:
        """Determine if request logging should be skipped."""
        # Skip health check endpoints
        if request.endpoint in ["health_check", "root"]:
            return True

        # Skip static files
        if request.endpoint and request.endpoint.startswith("static"):
            return True

        # Skip Swagger UI files
        return bool(request.path.startswith("/openapi/"))

    def _extract_request_data(self) -> dict[str, Any]:
        """Extract relevant request data for logging."""
        data = {
            "method": request.method,
            "url": request.url,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", ""),
        }

        # Add authenticated user info if available
        if hasattr(g, "current_user_id") and g.current_user_id:
            data["user_id"] = g.current_user_id

        # Add request body size for non-GET requests
        if request.method != "GET":
            data["content_length"] = request.content_length or 0
            data["content_type"] = request.content_type or ""

        # Add query parameters if present
        if request.args:
            data["query_params"] = dict(request.args)

        return data

    def _extract_response_data(self, response, duration: float) -> dict[str, Any]:
        """Extract relevant response data for logging."""
        return {
            "status_code": response.status_code,
            "content_length": response.content_length or 0,
            "duration_ms": round(duration * 1000, 2),
            "content_type": response.content_type or "",
        }


def get_request_id() -> str:
    """Get the current request ID."""
    return getattr(g, "request_id", "unknown")


def get_request_duration() -> float:
    """Get the current request duration in seconds."""
    start_time = getattr(g, "start_time", None)
    if start_time:
        return time.time() - start_time
    return 0.0


# Create a proxy for easy access to request ID
current_request_id = LocalProxy(get_request_id)
