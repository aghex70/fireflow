"""User repository interface."""

from abc import ABC, abstractmethod

from src.domain.entities.auth.user import User


class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""

    @abstractmethod
    def get_all(self) -> list[User]:
        """Get all users."""

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user."""

    @abstractmethod
    def get_by_role(self, role: str) -> list[User]:
        """Get users by role."""
