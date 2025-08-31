"""Health check controller for monitoring system status."""

import logging
from datetime import datetime, timezone

from flask import jsonify
from flask_openapi3 import APIBlueprint


logger = logging.getLogger(__name__)

health_bp = APIBlueprint("health", __name__)


@health_bp.get("/health", responses={200: {"description": "Health check successful"}})
def health_check():
    """Basic health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "FireFlow",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ), 200
