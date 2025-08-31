"""Authentication Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    """Schema for user login."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username (minimum 3 characters)"
    )
    password: str = Field(
        ..., min_length=8, description="Password (minimum 8 characters)"
    )


class RegisterSchema(BaseModel):
    """Schema for user registration."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username (minimum 3 characters)"
    )
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(
        ..., min_length=8, description="Password (minimum 8 characters)"
    )
    full_name: str | None = Field(None, max_length=255, description="Full name")
    role: Literal["admin", "operator", "viewer"] = Field(
        default="viewer", description="User role"
    )


class RefreshTokenSchema(BaseModel):
    """Schema for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")


class ChangePasswordSchema(BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (minimum 8 characters)"
    )


class UpdateRolesSchema(BaseModel):
    """Schema for updating user roles."""

    role: Literal["admin", "operator", "viewer"] = Field(..., description="User role")


class TokenResponseSchema(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int | None = Field(None, description="Token expiration in seconds")


class UserResponseSchema(BaseModel):
    """Schema for user response."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str | None = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    status: str = Field(..., description="User status")


class LoginResponseSchema(BaseModel):
    """Schema for login response."""

    user: UserResponseSchema = Field(..., description="User information")
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class AuthErrorSchema(BaseModel):
    """Schema for authentication errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict | None = Field(None, description="Additional error details")


class CurrentUserResponseSchema(BaseModel):
    """Schema for current user response."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str | None = Field(None, description="Full name")
    role: str = Field(..., description="User role")
    status: str = Field(..., description="User status")


class SuccessResponseSchema(BaseModel):
    """Schema for success responses."""

    message: str = Field(..., description="Success message")
    success: bool = Field(default=True, description="Success flag")


class AuthUseCaseEnum(str, Enum):
    """Enum for authentication use cases."""

    GET_CURRENT_USER = "get_current_user"
    LOGIN = "login"
    REFRESH_TOKEN = "refresh_token"  # noqa: S105
    REGISTER_USER = "register_user"
