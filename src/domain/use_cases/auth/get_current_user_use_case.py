"""Get current user use case."""

from typing import Any

from src.domain.services.auth.service import UserService


class GetCurrentUserUseCase:
    """Use case for getting current user info."""

    def __init__(self, user_service: UserService):
        """Initialize use case."""
        self.user_service = user_service

    def execute(self, user_id: int) -> dict[str, Any]:
        """Execute get current user."""
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
