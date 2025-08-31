from enum import Enum

from pydantic import BaseModel, Field

from src.domain.entities.filtering_policy.filtering_policy import (
    PolicyActionEnum,
    PolicyStatusEnum,
)
from src.infrastructure.web.utils.pagination import PaginatedResponseSchema


class FilteringPolicyCreateSchema(BaseModel):
    """Schema for creating a filtering policy."""

    name: str = Field(..., min_length=1, max_length=100, description="Policy name")
    description: str | None = Field(
        None,
        max_length=500,
        description="Policy description",
    )
    priority: int = Field(
        100,
        ge=0,
        description="Priority level (lower = higher priority)",
    )
    action: PolicyActionEnum = Field(
        PolicyActionEnum.ALLOW,
        description="Policy action",
    )
    status: PolicyStatusEnum = Field(
        default=PolicyStatusEnum.ACTIVE, description="Whether the policy is enabled"
    )


class FilteringPolicyResponseSchema(BaseModel):
    """Schema for filtering policy response."""

    id: int
    firewall_id: int
    name: str
    description: str | None
    priority: int
    action: PolicyActionEnum
    status: PolicyStatusEnum


class PaginatedFilteringPolicyResponseSchema(PaginatedResponseSchema):
    """Schema for paginated filtering policy responses."""

    items: list[FilteringPolicyResponseSchema] = Field(
        description="Policies for current page"
    )


class FilteringPolicyUseCaseEnum(str, Enum):
    """Schema for filtering policy use case enum."""

    GET_ALL_FILTERING_POLICIES = "get_all_filtering_policies"
    GET_FILTERING_POLICY_BY_ID = "get_filtering_policy_by_id"
    CREATE_FILTERING_POLICY = "create_filtering_policy"
    DELETE_FILTERING_POLICY = "delete_filtering_policy"
    GET_POLICIES_BY_FIREWALL = "get_policies_by_firewall"
