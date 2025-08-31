"""Authentication controller."""

import logging

from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag
from pydantic import ValidationError

from src.domain.use_cases.auth.factory import build_auth_use_case
from src.infrastructure.auth.middleware import (
    get_current_user_id,
    require_auth,
)
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.web.schemas.auth.auth_schemas import (
    AuthUseCaseEnum,
    CurrentUserResponseSchema,
    LoginResponseSchema,
    LoginSchema,
    RefreshTokenSchema,
    RegisterSchema,
    UserResponseSchema,
)
from src.infrastructure.web.schemas.common.openapi_schemas import ErrorResponseSchema
from src.infrastructure.web.utils.response import build_error_500_response


logger = logging.getLogger(__name__)


# Create blueprint with OpenAPI tags
auth_tag = Tag(name="auth", description="Authentication endpoints")

auth_bp = APIBlueprint("auth", __name__, url_prefix="/api/v1/auth", abp_tags=[auth_tag])


@auth_bp.post(
    "/register",
    responses={
        201: UserResponseSchema,
        400: ErrorResponseSchema,
        409: ErrorResponseSchema,
    },
)
def register(body: RegisterSchema):
    """Register a new user."""
    try:
        # Create user using the use case
        with get_db_session() as session:
            use_case = build_auth_use_case(AuthUseCaseEnum.REGISTER_USER, session)
            user = use_case.execute(body)
            user_response = UserResponseSchema.model_validate(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "status": user.status.value
                }
            )

            return jsonify(
                {
                    "message": "User registered successfully",
                    "user": user_response.model_dump(),
                }
            ), 201

    except ValidationError as e:
        return jsonify(
            {
                "error": "Validation error",
                "message": "Invalid input data",
                "details": e.errors(),
            }
        ), 400
    except ValueError as e:
        return jsonify({"error": "Registration failed", "message": str(e)}), 409
    except Exception:
        logger.exception("Exception occurred during registration")
        return build_error_500_response()


@auth_bp.post(
    "/login",
    responses={
        200: LoginResponseSchema,
        400: ErrorResponseSchema,
        401: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
def login(body: LoginSchema):
    """User login."""
    try:
        # Authenticate user
        with get_db_session() as session:
            use_case = build_auth_use_case(AuthUseCaseEnum.LOGIN, session)
            result = use_case.execute(body)
            login_response = LoginResponseSchema.model_validate(result)
            return jsonify(login_response.model_dump()), 200

    except ValidationError as e:
        return jsonify(
            {
                "error": "Validation error",
                "message": "Invalid input data",
                "details": e.errors(),
            }
        ), 400
    except ValueError as e:
        return jsonify({"error": "Authentication failed", "message": str(e)}), 401
    except Exception:
        logger.exception("Exception occurred during login")
        return build_error_500_response()


@auth_bp.post(
    "/refresh",
    responses={
        200: {"description": "Token refreshed successfully"},
        400: ErrorResponseSchema,
        401: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
def refresh_token(body: RefreshTokenSchema):
    """Refresh access token."""
    try:
        # Refresh token
        with get_db_session() as session:
            use_case = build_auth_use_case(AuthUseCaseEnum.REFRESH_TOKEN, session)
            result = use_case.execute(body)
            return jsonify(result), 200

    except ValidationError as e:
        return jsonify(
            {
                "error": "Validation error",
                "message": "Invalid input data",
                "details": e.errors(),
            }
        ), 400
    except ValueError as e:
        return jsonify({"error": "Token refresh failed", "message": str(e)}), 401
    except Exception:
        logger.exception("Exception occurred during token refresh")
        return build_error_500_response()


@auth_bp.get(
    "/me",
    responses={
        200: CurrentUserResponseSchema,
        401: ErrorResponseSchema,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
    security=[{"bearerAuth": []}],
)
@require_auth
def get_current_user():
    """Get current user information."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify(
                {"error": "Authentication required", "message": "No user ID found"}
            ), 401

        with get_db_session() as session:
            use_case = build_auth_use_case(AuthUseCaseEnum.GET_CURRENT_USER, session)
            result = use_case.execute(user_id)

            # Create response using Pydantic schema
            user_response = CurrentUserResponseSchema.model_validate(result)
            return jsonify(user_response.model_dump()), 200

    except ValueError as e:
        return jsonify({"error": "User not found", "message": str(e)}), 404
    except Exception:
        logger.exception("Exception occurred during current user retrieval")
        return build_error_500_response()
