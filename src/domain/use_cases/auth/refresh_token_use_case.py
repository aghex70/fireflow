"""Refresh token use case."""

from typing import Any

from src.domain.services.auth.service import UserService
from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.web.schemas.auth.auth_schemas import RefreshTokenSchema


class RefreshTokenUseCase:
    """Use case for refreshing access tokens."""

    def __init__(self, user_service: UserService, jwt_service: JWTService):
        """Initialize use case."""
        self.user_service = user_service
        self.jwt_service = jwt_service

    def execute(self, schema: RefreshTokenSchema) -> dict[str, Any]:
        """Execute token refresh."""
        refresh_token = schema.refresh_token
        # Validate refresh token
        if not self.jwt_service.is_token_valid(refresh_token):
            raise ValueError("Invalid refresh token")

        if not self.jwt_service.is_refresh_token(refresh_token):
            raise ValueError("Token is not a refresh token")

        # Get user from token
        user_id = self.jwt_service.get_user_id_from_token(refresh_token)
        if not user_id:
            raise ValueError("Invalid token payload")

        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Check if user can still login
        if not user.can_login():
            raise ValueError("User account is not active")

        # Generate new tokens
        return self.jwt_service.create_token_pair(user)
