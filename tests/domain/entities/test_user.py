"""Tests for User domain entity."""

from datetime import datetime

import pytest

from src.domain.entities.auth.user import User, UserRole, UserStatus


class TestUser:
    """Test cases for User entity."""

    def test_user_creation_with_required_fields(self):
        """Test user creation with required fields."""
        user = User(
            username="testuser",
            email="test@example.com"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == ""
        assert user.role == UserRole.VIEWER  # Default value
        assert user.status == UserStatus.ACTIVE  # Default value
        assert user.id is None
        assert user.full_name is None
        assert user.last_login is None

    def test_user_creation_with_all_fields(self):
        """Test user creation with all fields specified."""
        login_time = datetime.now()
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash="hashed_password",
            full_name="Admin User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            last_login=login_time
        )

        assert user.id == 1
        assert user.username == "admin"
        assert user.email == "admin@example.com"
        assert user.password_hash == "hashed_password"
        assert user.full_name == "Admin User"
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE
        assert user.last_login == login_time

    @pytest.mark.parametrize("role", [
        UserRole.ADMIN,
        UserRole.OPERATOR,
        UserRole.VIEWER
    ])
    def test_user_with_different_roles(self, role):
        """Test user creation with different roles."""
        user = User(
            username="testuser",
            email="test@example.com",
            role=role
        )

        assert user.role == role

    @pytest.mark.parametrize("status", [
        UserStatus.ACTIVE,
        UserStatus.INACTIVE,
        UserStatus.SUSPENDED
    ])
    def test_user_with_different_statuses(self, status):
        """Test user creation with different statuses."""
        user = User(
            username="testuser",
            email="test@example.com",
            status=status
        )

        assert user.status == status

    def test_user_set_password(self):
        """Test password setting functionality."""
        user = User(
            username="testuser",
            email="test@example.com"
        )

        user.set_password("mypassword123")

        assert user.password_hash != ""
        assert user.password_hash != "mypassword123"  # Should be hashed
        assert ":" in user.password_hash  # Should contain salt separator

    def test_user_check_password(self):
        """Test password checking functionality."""
        user = User(
            username="testuser",
            email="test@example.com"
        )

        password = "mypassword123"
        user.set_password(password)

        # Correct password should return True
        assert user.check_password(password) is True

        # Incorrect password should return False
        assert user.check_password("wrongpassword") is False

    def test_user_check_password_empty_hash(self):
        """Test password checking with empty hash."""
        user = User(
            username="testuser",
            email="test@example.com"
        )

        # No password set, should return False
        assert user.check_password("anypassword") is False

    def test_user_is_active(self):
        """Test is_active method."""
        active_user = User(
            username="active",
            email="active@example.com",
            status=UserStatus.ACTIVE
        )

        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            status=UserStatus.INACTIVE
        )

        suspended_user = User(
            username="suspended",
            email="suspended@example.com",
            status=UserStatus.SUSPENDED
        )

        assert active_user.is_active() is True
        assert inactive_user.is_active() is False
        assert suspended_user.is_active() is False

    def test_user_can_login(self):
        """Test can_login method."""
        active_user = User(
            username="active",
            email="active@example.com",
            status=UserStatus.ACTIVE
        )

        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            status=UserStatus.INACTIVE
        )

        assert active_user.can_login() is True
        assert inactive_user.can_login() is False

    def test_user_equality(self):
        """Test user equality comparison."""
        user1 = User(
            id=1,
            username="testuser",
            email="test@example.com"
        )

        user2 = User(
            id=1,
            username="testuser",
            email="test@example.com"
        )

        user3 = User(
            id=2,
            username="testuser",
            email="test@example.com"
        )

        assert user1 == user2
        assert user1 != user3

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com"
        )

        str_repr = str(user)
        assert "testuser" in str_repr or "test@example.com" in str_repr

    def test_user_role_enum_values(self):
        """Test that role enum has correct values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.OPERATOR.value == "operator"
        assert UserRole.VIEWER.value == "viewer"

    def test_user_status_enum_values(self):
        """Test that status enum has correct values."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"

    def test_user_default_values(self):
        """Test that user uses correct default values."""
        user = User(
            username="testuser",
            email="test@example.com"
        )

        assert user.role == UserRole.VIEWER
        assert user.status == UserStatus.ACTIVE
        assert user.password_hash == ""

    def test_password_hashing_is_unique(self):
        """Test that password hashing produces unique hashes."""
        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")

        password = "samepassword"
        user1.set_password(password)
        user2.set_password(password)

        # Same password should produce different hashes due to salt
        assert user1.password_hash != user2.password_hash

        # But both should validate correctly
        assert user1.check_password(password) is True
        assert user2.check_password(password) is True