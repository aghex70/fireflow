"""Tests for Auth use cases."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.domain.entities.auth.user import User, UserRole, UserStatus
from src.domain.use_cases.auth.get_current_user_use_case import GetCurrentUserUseCase
from src.domain.use_cases.auth.login_use_case import LoginUseCase
from src.domain.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase
from src.domain.use_cases.auth.register_user_use_case import RegisterUserUseCase
from src.infrastructure.web.schemas.auth.auth_schemas import (
    LoginSchema,
    RefreshTokenSchema,
    RegisterSchema,
)


class TestLoginUseCase:
    """Test cases for LoginUseCase."""

    def test_login_success(self):
        """Test successful user login."""
        # Arrange
        mock_user_service = Mock()
        mock_jwt_service = Mock()
        
        authenticated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE
        )
        mock_user_service.authenticate_user.return_value = authenticated_user
        mock_jwt_service.create_token_pair.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
        }

        use_case = LoginUseCase(mock_user_service, mock_jwt_service)
        schema = LoginSchema(username="testuser", password="password123")

        # Act
        result = use_case.execute(schema)

        # Assert
        assert result["user"]["id"] == 1
        assert result["user"]["username"] == "testuser"
        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        mock_user_service.authenticate_user.assert_called_once_with("testuser", "password123")
        mock_jwt_service.create_token_pair.assert_called_once_with(authenticated_user)

    def test_login_invalid_credentials_raises_error(self):
        """Test login with invalid credentials raises error."""
        # Arrange
        mock_user_service = Mock()
        mock_jwt_service = Mock()
        mock_user_service.authenticate_user.return_value = None

        use_case = LoginUseCase(mock_user_service, mock_jwt_service)
        schema = LoginSchema(username="testuser", password="wrongpassword")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid username or password"):
            use_case.execute(schema)


class TestRegisterUserUseCase:
    """Test cases for RegisterUserUseCase."""

    def test_register_user_success(self):
        """Test successful user registration."""
        # Arrange
        mock_user_service = Mock()
        
        mock_user_service.get_user_by_username.return_value = None
        mock_user_service.get_user_by_email.return_value = None
        
        registered_user = User(
            id=1,
            username="newuser",
            email="new@example.com",
            full_name="New User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
        )
        mock_user_service.create_user.return_value = registered_user

        use_case = RegisterUserUseCase(mock_user_service)
        schema = RegisterSchema(
            username="newuser",
            email="new@example.com",
            password="password123",
            full_name="New User",
        )

        # Act
        result = use_case.execute(schema)

        # Assert
        assert result.id == 1
        assert result.username == "newuser"
        mock_user_service.create_user.assert_called_once()

    def test_register_user_existing_username_raises_error(self):
        """Test registration with existing username raises error."""
        # Arrange
        mock_user_service = Mock()
        
        existing_user = User(
            id=1,
            username="existinguser",
            email="existing@example.com",
            full_name="Existing User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
        )
        mock_user_service.get_user_by_username.return_value = existing_user

        use_case = RegisterUserUseCase(mock_user_service)
        schema = RegisterSchema(
            username="existinguser",
            email="new@example.com",
            password="password123",
            full_name="New User",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Username 'existinguser' already exists"):
            use_case.execute(schema)


class TestRefreshTokenUseCase:
    """Test cases for RefreshTokenUseCase."""

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Arrange
        mock_user_service = Mock()
        mock_jwt_service = Mock()
        
        mock_jwt_service.is_refresh_token.return_value = True
        mock_jwt_service.get_user_id_from_token.return_value = 1
        
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
        )
        mock_user_service.get_user_by_id.return_value = user
        mock_jwt_service.create_token_pair.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
        }

        use_case = RefreshTokenUseCase(mock_user_service, mock_jwt_service)
        schema = RefreshTokenSchema(refresh_token="valid_refresh_token")

        # Act
        result = use_case.execute(schema)

        # Assert
        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"
        mock_jwt_service.is_refresh_token.assert_called_once_with("valid_refresh_token")
        mock_user_service.get_user_by_id.assert_called_once_with(1)

    def test_refresh_token_invalid_token_raises_error(self):
        """Test refresh with invalid token raises error."""
        # Arrange
        mock_user_service = Mock()
        mock_jwt_service = Mock()
        mock_jwt_service.is_refresh_token.return_value = False

        use_case = RefreshTokenUseCase(mock_user_service, mock_jwt_service)
        schema = RefreshTokenSchema(refresh_token="invalid_token")

        # Act & Assert
        with pytest.raises(ValueError, match="Token is not a refresh token"):
            use_case.execute(schema)


class TestGetCurrentUserUseCase:
    """Test cases for GetCurrentUserUseCase."""

    def test_get_current_user_success(self):
        """Test successful current user retrieval."""
        # Arrange
        mock_user_service = Mock()
        
        current_user = Mock()
        current_user.id = 1
        current_user.username = "currentuser"
        current_user.email = "current@example.com"
        current_user.full_name = "Current User"
        current_user.role = UserRole.VIEWER
        current_user.status = UserStatus.ACTIVE
        current_user.created_at = None
        mock_user_service.get_user_by_id.return_value = current_user

        use_case = GetCurrentUserUseCase(mock_user_service)

        # Act
        result = use_case.execute(1)

        # Assert
        assert result["id"] == 1
        assert result["username"] == "currentuser"
        assert result["role"] == "viewer"
        mock_user_service.get_user_by_id.assert_called_once_with(1)

    def test_get_current_user_invalid_token_raises_error(self):
        """Test get current user with invalid user ID raises error."""
        # Arrange
        mock_user_service = Mock()
        mock_user_service.get_user_by_id.return_value = None

        use_case = GetCurrentUserUseCase(mock_user_service)

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            use_case.execute(999)

    # Removed duplicate test - covered by test_get_current_user_invalid_token_raises_error
