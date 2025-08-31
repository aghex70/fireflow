import logging

from src.domain.entities.auth.user import User
from src.domain.repositories.auth.user_repository import UserRepository


logger = logging.getLogger(__name__)


class UserService:
    """Service class for managing user-related operations."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user: User) -> User:
        """Create a new user."""
        return self.repository.create(user)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.repository.get_by_email(email)

    def authenticate_user(self, username: str, password: str) -> User | None:
        """Authenticate a user by username or email."""
        # Try username first, then email
        user = self.repository.get_by_username(username)
        if not user:
            user = self.repository.get_by_email(username)

        if user and user.can_login() and user.check_password(password):
            return user
        return None
