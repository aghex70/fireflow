"""JWT authentication service."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from src.domain.entities.auth.user import User, UserRole
from src.infrastructure.config.settings import get_settings


logger = logging.getLogger(__name__)


class JWTService:
    """Service for handling JWT tokens."""

    def __init__(self, settings=None):
        """Initialize JWT service."""
        self.settings = settings or get_settings()
        self.secret_key = self.settings.jwt.secret_key
        self.algorithm = self.settings.jwt.algorithm
        self.access_token_expire_minutes = self.settings.jwt.access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.jwt.refresh_token_expire_days

    def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "iat": now,
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user: User) -> str:
        """Create refresh token for user."""
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "iat": now,
            "exp": now + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode token."""
        logger.info(token)
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.info(payload)
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id_from_token(self, token: str) -> int | None:
        """Extract user ID from token."""
        payload = self.verify_token(token)
        if payload and "sub" in payload:
            try:
                return int(payload["sub"])
            except (ValueError, TypeError):
                return None
        return None

    def get_user_role_from_token(self, token: str) -> UserRole | None:
        """Extract user role from token."""
        payload = self.verify_token(token)
        if payload and "role" in payload:
            try:
                return UserRole(payload["role"])
            except (ValueError, TypeError):
                return None
        return None

    def is_token_valid(self, token: str) -> bool:
        """Check if token is valid."""
        return self.verify_token(token) is not None

    def is_access_token(self, token: str) -> bool:
        """Check if token is an access token."""
        payload = self.verify_token(token)
        return payload is not None and payload.get("type") == "access"

    def is_refresh_token(self, token: str) -> bool:
        """Check if token is a refresh token."""
        payload = self.verify_token(token)
        return payload is not None and payload.get("type") == "refresh"

    def create_token_pair(self, user: User) -> dict[str, str]:
        """Create access and refresh token pair."""
        return {
            "access_token": self.create_access_token(user),
            "refresh_token": self.create_refresh_token(user),
            "token_type": "bearer",
        }
