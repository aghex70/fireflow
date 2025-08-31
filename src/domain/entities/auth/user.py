"""User domain entity."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles enum."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """Domain entity representing a user."""

    username: str
    email: str
    password_hash: str = ""
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.ACTIVE
    id: int | None = None
    full_name: str | None = None

    def set_password(self, password: str) -> None:
        """Set password hash."""
        salt = secrets.token_hex(16)
        self.password_hash = (
            hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            ).hex()
            + ":"
            + salt
        )

    def check_password(self, password: str) -> bool:
        """Check if password is correct."""
        if ":" not in self.password_hash:
            return False

        password_hash, salt = self.password_hash.split(":")
        return (
            password_hash
            == hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            ).hex()
        )

    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    def can_login(self) -> bool:
        """Check if user can login."""
        return self.is_active()
