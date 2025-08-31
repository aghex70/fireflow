"""User registration use case."""

import logging

from src.domain.entities.auth.user import User, UserRole, UserStatus
from src.domain.services.auth.service import UserService
from src.infrastructure.web.schemas.auth.auth_schemas import RegisterSchema


logger = logging.getLogger(__name__)


class RegisterUserUseCase:
    """Use case for user registration."""

    def __init__(self, user_service: UserService):
        """Initialize use case."""
        self.user_service = user_service

    def execute(
        self,
        schema: RegisterSchema,
    ) -> User:
        """Execute user registration."""
        logger.info(
            f"User registration attempt for username: {schema.username}, email: {schema.email}"
        )

        # Check if user already exists
        if self.user_service.get_user_by_username(schema.username):
            logger.warning(
                f"Registration failed - username already exists: {schema.username}"
            )
            raise ValueError(f"Username '{schema.username}' already exists")

        if self.user_service.get_user_by_email(schema.email):
            logger.warning(
                f"Registration failed - email already exists: {schema.email}"
            )
            raise ValueError(f"Email '{schema.email}' already exists")

        # Create user
        user = User(
            username=schema.username.strip(),
            email=schema.email.strip().lower(),
            full_name=schema.full_name.strip() if schema.full_name else None,
            role=UserRole(schema.role),
            status=UserStatus.ACTIVE,
        )

        user.set_password(schema.password)
        return self.user_service.create_user(user)
