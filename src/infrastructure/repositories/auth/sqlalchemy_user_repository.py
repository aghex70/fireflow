"""SQLAlchemy implementation of User repository."""

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.entities.auth.user import User, UserRole, UserStatus
from src.domain.repositories.auth.user_repository import UserRepository
from src.infrastructure.database.models import SQLUser


logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create(self, user: User) -> User:
        """Create a new user."""
        try:
            db_user = SQLUser(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                full_name=user.full_name,
                status=user.status.value,
                last_login=user.last_login,
                role=user.role.value,
            )

            self.session.add(db_user)
            self.session.flush()  # Get the ID

            # Don't commit here - let the calling code handle transaction
            return self._to_entity(db_user)

        except IntegrityError as e:
            # Don't rollback here - let the calling code handle transaction
            error_str = str(e).lower()
            # Check for specific constraint violations (more specific first)
            if "users.email" in error_str:
                raise ValueError(f"Email '{user.email}' already exists") from e
            elif "users.username" in error_str:
                raise ValueError(f"Username '{user.username}' already exists") from e
            elif "email" in error_str and "constraint" in error_str:
                raise ValueError(f"Email '{user.email}' already exists") from e
            elif "username" in error_str and "constraint" in error_str:
                raise ValueError(f"Username '{user.username}' already exists") from e
            raise ValueError("User creation failed due to constraint violation") from e

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        db_user = self.session.query(SQLUser).filter(SQLUser.id == user_id).first()
        return self._to_entity(db_user) if db_user else None

    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        db_user = (
            self.session.query(SQLUser).filter(SQLUser.username == username).first()
        )
        return self._to_entity(db_user) if db_user else None

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        db_user = self.session.query(SQLUser).filter(SQLUser.email == email).first()
        return self._to_entity(db_user) if db_user else None

    def get_all(self) -> list[User]:
        """Get all users."""
        db_users = self.session.query(SQLUser).all()
        return [self._to_entity(db_user) for db_user in db_users]

    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        db_user = self.session.query(SQLUser).filter(SQLUser.id == user_id).first()
        if not db_user:
            return False

        # Delete user (no separate role table anymore)
        self.session.delete(db_user)
        # Don't commit here - let the calling code handle transaction
        return True

    def get_by_role(self, role: str) -> list[User]:
        """Get users by role."""
        db_users = self.session.query(SQLUser).filter(SQLUser.role == role).all()
        return [self._to_entity(db_user) for db_user in db_users]

    def _to_entity(self, db_user: SQLUser) -> User:
        """Convert database model to domain entity."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash,
            full_name=db_user.full_name,
            role=UserRole(db_user.role),
            status=UserStatus(db_user.status),
            last_login=db_user.last_login,
        )
