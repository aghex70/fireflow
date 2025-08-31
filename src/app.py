import logging

from flask_cors import CORS
from flask_openapi3 import OpenAPI

from src.infrastructure.celery.celery_app import make_celery
from src.infrastructure.config.logging_config import setup_logging
from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.connection import create_tables
from src.infrastructure.web.controllers.auth.auth_controller import auth_bp
from src.infrastructure.web.controllers.filtering_policy.filtering_policy_controller import (
    policy_bp,
)
from src.infrastructure.web.controllers.firewall.firewall_controller import firewall_bp
from src.infrastructure.web.controllers.firewall_rule.firewall_rule_controller import (
    rule_bp,
)
from src.infrastructure.web.controllers.health_controller import health_bp
from src.infrastructure.web.controllers.task_controller import task_bp
from src.infrastructure.web.middleware.error_handler import ErrorHandler
from src.infrastructure.web.middleware.logging_middleware import (
    RequestLoggingMiddleware,
)


def create_app():
    """Create and configure the Flask application."""
    # Load settings from .env file
    settings = get_settings()

    # Configure logging first
    setup_logging(settings.logging)
    logger = logging.getLogger(__name__)
    logger.info("Starting FireFlow application...")

    # Create OpenAPI app
    info = {
        "title": "FireFlow API",
        "version": settings.app_version,
        "description": "Firewall Management System API with OpenAPI 3.0 documentation",
    }

    # Define security schemes for OpenAPI documentation
    security_schemes = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /api/v1/auth/login endpoint",
        }
    }

    app = OpenAPI(
        __name__, info=info, doc_prefix="/apidocs", security_schemes=security_schemes
    )

    # Configuration from settings
    app.config["SECRET_KEY"] = settings.flask_secret_key
    app.config["DEBUG"] = settings.debug
    app.config["DEBUG"] = settings.debug

    # Configure Flask app logging
    setup_logging(settings.logging, app)

    # Enable CORS
    CORS(app)

    logger.info(
        f"Flask app configured - Debug: {settings.debug}, Environment: {settings.environment}"
    )

    # Initialize middleware
    ErrorHandler(app)
    RequestLoggingMiddleware(app)

    # Register API blueprints (all are now APIBlueprints)
    app.register_api(health_bp)
    app.register_api(auth_bp)
    app.register_api(firewall_bp)
    app.register_api(policy_bp)
    app.register_api(rule_bp)
    app.register_api(task_bp)

    # Root endpoint
    @app.route("/")
    def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "documentation": "/apidocs/",
            "health_checks": {
                "basic": "/health",
                "detailed": "/health/detailed",
                "readiness": "/health/ready",
                "liveness": "/health/live",
            },
            "endpoints": {
                "auth": "/api/v1/auth",
                "firewalls": "/api/v1/firewalls",
                "policies": "/api/v1/policies",
                "rules": "/api/v1/rules",
                "tasks": "/api/v1/tasks",
            },
        }, 200

    # Create database tables
    create_tables()

    # Initialize Celery with Flask context
    celery = make_celery(app)
    app.celery = celery

    logger.info("FireFlow application initialization completed successfully")
    return app


if __name__ == "__main__":
    settings = get_settings()
    app = create_app()
    # app.run(debug=settings.debug, host=settings.flask_host, port=settings.flask_port)
    app.run(
        debug=True,
        host=settings.flask_host,
        port=settings.flask_port,
        use_reloader=True,
    )
