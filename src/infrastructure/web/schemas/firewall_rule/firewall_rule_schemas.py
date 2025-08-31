from enum import Enum
from ipaddress import ip_network

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.entities.firewall_rule.firewall_rule import (
    RuleActionEnum,
    RuleProtocolEnum,
)
from src.infrastructure.web.utils.pagination import PaginatedResponseSchema


class FirewallRuleCreateSchema(BaseModel):
    """Schema for creating a firewall rule."""

    order_index: int = Field(..., description="Rule order (lower = higher priority)")
    source_cidr: str | None = Field(
        None, max_length=43, description="Source CIDR block"
    )
    destination_cidr: str | None = Field(
        None,
        max_length=43,
        description="Destination CIDR block",
    )
    protocol: RuleProtocolEnum = Field(
        RuleProtocolEnum.TCP,
        description="Protocol type",
    )
    source_port_minimum: int | None = Field(
        None, ge=1, le=65535, description="Minimum source port"
    )
    source_port_maximum: int | None = Field(
        None, ge=1, le=65535, description="Maximum source port"
    )
    destination_port_minimum: int | None = Field(
        None, ge=1, le=65535, description="Minimum destination port"
    )
    destination_port_maximum: int | None = Field(
        None, ge=1, le=65535, description="Maximum destination port"
    )
    action: RuleActionEnum = Field(RuleActionEnum.ALLOW, description="Rule action")

    @field_validator("source_cidr", "destination_cidr")
    @classmethod
    def validate_cidr(cls, v):
        """Validate and normalize CIDR blocks."""
        if v is None or str(v).strip() == "":
            return None
        try:
            return str(ip_network(v, strict=False))
        except Exception as e:
            raise ValueError(
                f"Invalid CIDR format. Must be valid IPv4/IPv6 CIDR (e.g. 10.0.0.0/24 or ::/0). Received: {v}"
            ) from e

    @model_validator(mode="after")
    def validate_port_ranges(self):
        """Validate port range logic."""
        # Source port range validation
        if (self.source_port_minimum is not None) != (
            self.source_port_maximum is not None
        ):
            raise ValueError(
                "Source port minimum and maximum must both be specified or both be None"
            )
        if (
            self.source_port_minimum is not None
            and self.source_port_maximum is not None
            and self.source_port_minimum > self.source_port_maximum
        ):
            raise ValueError("Source port minimum cannot be greater than maximum")

        # Destination port range validation
        if (self.destination_port_minimum is not None) != (
            self.destination_port_maximum is not None
        ):
            raise ValueError(
                "Destination port minimum and maximum must both be specified or both be None"
            )
        if (
            self.destination_port_minimum is not None
            and self.destination_port_maximum is not None
            and self.destination_port_minimum > self.destination_port_maximum
        ):
            raise ValueError("Destination port minimum cannot be greater than maximum")

        return self

    @model_validator(mode="after")
    def _raise_ip_version_error(self) -> None:
        """Raise IP version consistency error."""
        raise ValueError(
            "Source and destination CIDR blocks must use the same IP version (both IPv4 or both IPv6)"
        )

    def validate_ip_family_consistency(self):
        """Validate IP family consistency between source and destination CIDRs."""
        if self.source_cidr and self.destination_cidr:
            try:
                source_net = ip_network(self.source_cidr, strict=False)
                dest_net = ip_network(self.destination_cidr, strict=False)
                if source_net.version != dest_net.version:
                    self._raise_ip_version_error()
            except Exception as e:
                # CIDR validation already handled by field validator
                if "Invalid CIDR format" not in str(e):
                    raise ValueError(f"IP family consistency check failed: {e}") from e
        return self


class FirewallRuleResponseSchema(BaseModel):
    """Schema for firewall rule response."""

    id: int
    policy_id: int
    order_index: int
    source_cidr: str | None
    destination_cidr: str | None
    protocol: str
    source_port_minimum: int | None
    source_port_maximum: int | None
    destination_port_minimum: int | None
    destination_port_maximum: int | None
    action: str


class FirewallRuleUseCaseEnum(str, Enum):
    """Schema for filtering policy use case enum."""

    GET_ALL_FIREWALL_RULES = "get_all_firewall_rules"
    GET_FIREWALL_RULE_BY_ID = "get_firewall_rule_by_id"
    CREATE_FIREWALL_RULE = "create_firewall_rule"
    DELETE_FIREWALL_RULE = "delete_firewall_rule"
    GET_FIREWALL_RULES_BY_POLICY_ID = "get_firewall_rules_by_policy_id"


class PaginatedFirewallRuleResponseSchema(PaginatedResponseSchema):
    """Schema for paginated firewall rule responses."""

    items: list[FirewallRuleResponseSchema] = Field(
        description="Firewall rules for current page"
    )
