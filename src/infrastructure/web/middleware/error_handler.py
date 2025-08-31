"""Error handling middleware for Flask application."""

import logging
import traceback
from typing import Any

from flask import Flask, jsonify, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for the Flask application."""

    def __init__(self, app: Flask = None):
        """Initialize error handler."""
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize error handling for Flask app."""
        self.app = app
        self._register_error_handlers()

    def _register_error_handlers(self):
        """Register error handlers with Flask app."""

        @self.app.errorhandler(ValidationError)
        def handle_validation_error(error: ValidationError):
            """Handle Pydantic validation errors."""
            logger.warning(
                "Validation error",
                endpoint=request.endpoint,
                method=request.method,
                errors=error.errors(),
            )
            return jsonify(
                {
                    "error": "Validation Error",
                    "message": "Invalid input data",
                    "details": error.errors(),
                    "status_code": 400,
                }
            ), 400

        @self.app.errorhandler(ValueError)
        def handle_value_error(error: ValueError):
            """Handle value errors from business logic."""
            logger.warning(
                "Business logic error",
                endpoint=request.endpoint,
                method=request.method,
                error=str(error),
            )
            return jsonify(
                {
                    "error": "Business Logic Error",
                    "message": str(error),
                    "status_code": 400,
                }
            ), 400

        @self.app.errorhandler(IntegrityError)
        def handle_integrity_error(error: IntegrityError):
            """Handle database integrity errors."""
            logger.exception(
                "Database integrity error",
                endpoint=request.endpoint,
                method=request.method,
                error=str(error.orig),
            )

            # Extract meaningful error messages
            error_msg = str(error.orig)
            if "UNIQUE constraint failed" in error_msg:
                if "username" in error_msg:
                    message = "Username already exists"
                elif "email" in error_msg:
                    message = "Email already exists"
                else:
                    message = "Duplicate entry detected"
            elif "FOREIGN KEY constraint failed" in error_msg:
                message = "Referenced resource does not exist"
            else:
                message = "Database constraint violation"

            return jsonify(
                {
                    "error": "Database Error",
                    "message": message,
                    "status_code": 409,
                }
            ), 409

        @self.app.errorhandler(SQLAlchemyError)
        def handle_sqlalchemy_error(error: SQLAlchemyError):
            """Handle general SQLAlchemy errors."""
            logger.exception(
                "Database error",
                endpoint=request.endpoint,
                method=request.method,
                error=str(error),
                traceback=traceback.format_exc(),
            )
            return jsonify(
                {
                    "error": "Database Error",
                    "message": "A database error occurred",
                    "status_code": 500,
                }
            ), 500

        @self.app.errorhandler(HTTPException)
        def handle_http_exception(error: HTTPException):
            """Handle HTTP exceptions."""
            logger.info(
                "HTTP exception",
                endpoint=request.endpoint,
                method=request.method,
                status_code=error.code,
                error=error.description,
            )
            return jsonify(
                {
                    "error": error.name,
                    "message": error.description,
                    "status_code": error.code,
                }
            ), error.code

        @self.app.errorhandler(404)
        def handle_not_found(_error):
            """Handle 404 errors."""
            logger.info(
                "Resource not found",
                endpoint=request.endpoint,
                method=request.method,
                url=request.url,
            )
            return jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "status_code": 404,
                }
            ), 404

        @self.app.errorhandler(405)
        def handle_method_not_allowed(_error):
            """Handle 405 errors."""
            logger.info(
                "Method not allowed",
                endpoint=request.endpoint,
                method=request.method,
                url=request.url,
            )
            return jsonify(
                {
                    "error": "Method Not Allowed",
                    "message": f"The {request.method} method is not allowed for this endpoint",
                    "status_code": 405,
                }
            ), 405

        @self.app.errorhandler(429)
        def handle_rate_limit_exceeded(_error):
            """Handle rate limit errors."""
            logger.warning(
                "Rate limit exceeded",
                endpoint=request.endpoint,
                method=request.method,
                client_ip=request.remote_addr,
            )
            return jsonify(
                {
                    "error": "Rate Limit Exceeded",
                    "message": "Too many requests. Please try again later.",
                    "status_code": 429,
                }
            ), 429

        @self.app.errorhandler(Exception)
        def handle_generic_exception(error: Exception):
            """Handle any unhandled exceptions."""
            logger.exception(
                "Unhandled exception",
                endpoint=request.endpoint,
                method=request.method,
                error=str(error),
                error_type=type(error).__name__,
                traceback=traceback.format_exc(),
            )

            # Don't expose internal errors in production
            if self.app.config.get("DEBUG", False):
                message = f"Internal server error: {error!s}"
                details = traceback.format_exc()
            else:
                message = "An internal server error occurred"
                details = None

            response_data = {
                "error": "Internal Server Error",
                "message": message,
                "status_code": 500,
            }

            if details:
                response_data["details"] = details

            return jsonify(response_data), 500


def create_error_response(
    error_type: str,
    message: str,
    status_code: int = 500,
    details: Any = None,
) -> tuple[dict, int]:
    """Create a standardized error response."""
    response_data = {
        "error": error_type,
        "message": message,
        "status_code": status_code,
    }

    if details:
        response_data["details"] = details

    return response_data, status_code
