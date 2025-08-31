"""Common OpenAPI schemas for flask-openapi3."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponseSchema(BaseModel):
    """Standard error response schema."""

    error: str = Field(description="Error type or title")
    message: str = Field(description="Human-readable error message")
    details: str | dict[str, Any] | list[Any] | None = Field(
        default=None, description="Additional error details"
    )
    status_code: int | None = Field(default=None, description="HTTP status code")


class FirewallIdPathSchema(BaseModel):
    """Schema for firewall ID path parameters."""

    firewall_id: int = Field(..., ge=1, description="Firewall ID")


class PolicyIdPathSchema(BaseModel):
    """Schema for policy ID path parameters."""

    policy_id: int = Field(..., ge=1, description="Policy ID")


class FirewallPolicyPathSchema(PolicyIdPathSchema):
    """Schema for firewall and policy ID path parameters."""

    firewall_id: int = Field(ge=1, description="Firewall ID")


class FirewallPolicyRulePathSchema(FirewallPolicyPathSchema):
    """Schema for firewall and rule ID path parameters."""

    rule_id: int = Field(ge=1, description="Rule ID")


class RuleIdPathSchema(BaseModel):
    """Schema for rule ID path parameters."""

    rule_id: int = Field(..., ge=1, description="Rule ID")


class TaskIdPathSchema(BaseModel):
    """Schema for task ID path parameters."""

    task_id: str = Field(..., description="Task ID")
