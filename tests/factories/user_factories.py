"""Polyfactory factories for user-related entities."""

from datetime import datetime, timedelta, timezone

from polyfactory.factories import DataclassFactory

from src.domain.entities.auth.user import User, UserRole, UserStatus


class UserFactory(DataclassFactory[User]):
    """Factory for creating User instances."""

    __model__ = User
    __check_model__ = False  
    
    # Only use valid database enum values
    status = UserStatus.ACTIVE

    @classmethod
    def admin_user(cls) -> User:
        """Create an admin user."""
        return cls.build(role=UserRole.ADMIN)

    @classmethod
    def operator_user(cls) -> User:
        """Create an operator user."""
        return cls.build(role=UserRole.OPERATOR)

    @classmethod
    def viewer_user(cls) -> User:
        """Create a viewer user."""
        return cls.build(role=UserRole.VIEWER)

    @classmethod
    def active_user(cls, role: UserRole | None = None) -> User:
        """Create an active user."""
        kwargs = {"status": UserStatus.ACTIVE}
        if role is not None:
            kwargs["role"] = role
        return cls.build(**kwargs)

    @classmethod
    def inactive_user(cls, role: UserRole | None = None) -> User:
        """Create an inactive user."""
        kwargs = {"status": UserStatus.INACTIVE}
        if role is not None:
            kwargs["role"] = role
        return cls.build(**kwargs)

    @classmethod
    def suspended_user(cls, role: UserRole | None = None) -> User:
        """Create a suspended user (using inactive status for database compatibility)."""
        kwargs = {"status": UserStatus.INACTIVE}
        if role is not None:
            kwargs["role"] = role
        return cls.build(**kwargs)

    @classmethod
    def user_with_recent_login(cls, role: UserRole | None = None) -> User:
        """Create a user with recent login."""
        recent_login = datetime.now(timezone.utc) - timedelta(hours=1)
        kwargs = {"last_login": recent_login}
        if role is not None:
            kwargs["role"] = role
        return cls.build(**kwargs)

    @classmethod
    def user_with_password(cls, password: str, role: UserRole | None = None) -> User:
        """Create a user with a specific password."""
        user = cls.build(role=role if role else UserRole.VIEWER)
        user.set_password(password)
        return user

    @classmethod
    def new_user(cls, role: UserRole | None = None) -> User:
        """Create a newly registered user."""
        now = datetime.now(timezone.utc)
        kwargs = {
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "status": UserStatus.ACTIVE,
        }
        if role is not None:
            kwargs["role"] = role
        return cls.build(**kwargs)
