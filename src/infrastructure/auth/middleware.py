"""Authentication middleware."""

import logging
from collections.abc import Callable
from functools import wraps

from flask import g, jsonify, request

from src.domain.entities.auth.user import UserRole
from src.infrastructure.auth.jwt_service import JWTService


logger = logging.getLogger(__name__)


def get_token_from_header() -> str | None:
    """Extract token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            return jsonify(
                {
                    "error": "Authentication required",
                    "message": "Missing authorization token",
                }
            ), 401

        jwt_service = JWTService()

        if not jwt_service.is_token_valid(token):
            return jsonify(
                {"error": "Invalid token", "message": "Token is invalid or expired"}
            ), 401

        if not jwt_service.is_access_token(token):
            return jsonify(
                {"error": "Invalid token type", "message": "Access token required"}
            ), 401

        # Store user info in Flask's g object
        user_id = jwt_service.get_user_id_from_token(token)
        user_role = jwt_service.get_user_role_from_token(token)

        g.current_user_id = user_id
        g.current_user_role = user_role
        g.current_token = token

        return f(*args, **kwargs)

    return decorated_function


def require_roles(required_roles: list[UserRole]) -> Callable:
    """Decorator to require specific roles."""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check authentication
            token = get_token_from_header()

            if not token:
                return jsonify(
                    {
                        "error": "Authentication required",
                        "message": "Missing authorization token",
                    }
                ), 401

            jwt_service = JWTService()
            logger.info(token)
            if not jwt_service.is_token_valid(token):
                return jsonify(
                    {"error": "Invalid token", "message": "Token is invalid or expired"}
                ), 401

            if not jwt_service.is_access_token(token):
                return jsonify(
                    {"error": "Invalid token type", "message": "Access token required"}
                ), 401

            # Check roles
            user_role = jwt_service.get_user_role_from_token(token)

            if user_role not in required_roles:
                return jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": f"Required roles: {[role.value for role in required_roles]}",
                    }
                ), 403

            # Store user info in Flask's g object
            user_id = jwt_service.get_user_id_from_token(token)

            g.current_user_id = user_id
            g.current_user_role = user_role
            g.current_token = token

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_admin(f: Callable) -> Callable:
    """Decorator to require admin role."""
    return require_roles([UserRole.ADMIN])(f)


def require_admin_or_operator(f: Callable) -> Callable:
    """Decorator to require admin or operator role."""
    return require_roles([UserRole.ADMIN, UserRole.OPERATOR])(f)


def get_current_user_id() -> int | None:
    """Get current user ID from Flask's g object."""
    return getattr(g, "current_user_id", None)


def get_current_user_role() -> UserRole | None:
    """Get current user role from Flask's g object."""
    return getattr(g, "current_user_role", None)

