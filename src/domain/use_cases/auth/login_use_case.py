"""User login use case."""

import logging
from typing import Any

from src.domain.services.auth.service import UserService
from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.web.schemas.auth.auth_schemas import LoginSchema


logger = logging.getLogger(__name__)


class LoginUseCase:
    """Use case for user login."""

    def __init__(self, user_service: UserService, jwt_service: JWTService):
        """Initialize use case."""
        self.user_service = user_service
        self.jwt_service = jwt_service

    def execute(self, schema: LoginSchema) -> dict[str, Any]:
        """Execute user login."""
        logger.info(f"Login attempt for username: {schema.username}")

        # Authenticate user using service (handles login attempts and validations)
        authenticated_user = self.user_service.authenticate_user(
            schema.username, schema.password
        )
        if not authenticated_user:
            raise ValueError("Invalid username or password")

        # Generate tokens
        tokens = self.jwt_service.create_token_pair(authenticated_user)

        logger.info(
            f"Login successful for user: {authenticated_user.username} (ID: {authenticated_user.id})"
        )

        return {
            "user": {
                "id": authenticated_user.id,
                "username": authenticated_user.username,
                "email": authenticated_user.email,
                "full_name": authenticated_user.full_name,
                "role": authenticated_user.role.value,
                "status": authenticated_user.status.value,
                "last_login": authenticated_user.last_login.isoformat()
                if authenticated_user.last_login
                else None,
            },
            **tokens,
        }
