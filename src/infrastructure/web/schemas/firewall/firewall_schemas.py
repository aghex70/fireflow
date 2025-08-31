from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.firewall.firewall import FirewallEnvironmentEnum
from src.infrastructure.web.utils.pagination import PaginatedResponseSchema


class FirewallCreateSchema(BaseModel):
    """Schema for creating a firewall."""

    name: str = Field(..., min_length=1, max_length=100, description="Firewall name")
    environment: FirewallEnvironmentEnum = Field(
        ..., description="Firewall environment"
    )
    scope: str = Field(..., max_length=50, description="Firewall scope")
    description: str | None = Field(
        None,
        max_length=500,
        description="Firewall description",
    )


class FirewallResponseSchema(BaseModel):
    """Schema for firewall response."""

    id: int
    name: str
    description: str | None
    environment: FirewallEnvironmentEnum
    scope: str
    model_config = ConfigDict(from_attributes=True)


class PaginatedFirewallResponseSchema(PaginatedResponseSchema):
    """Schema for paginated firewall responses."""

    items: list[FirewallResponseSchema] = Field(
        description="Firewalls for current page"
    )


class FirewallUseCaseEnum(str, Enum):
    """Schema for firewall use case enum."""

    GET_ALL_FIREWALLS = "get_all_firewalls"
    GET_FIREWALL_BY_ID = "get_firewall_by_id"
    CREATE_FIREWALL = "create_firewall"
    DELETE_FIREWALL = "delete_firewall"
