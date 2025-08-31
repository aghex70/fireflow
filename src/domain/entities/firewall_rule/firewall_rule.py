from dataclasses import dataclass
from enum import Enum


class RuleActionEnum(str, Enum):
    """Firewall rule action enum."""

    ALLOW = "allow"
    DENY = "deny"
    REJECT = "reject"


class RuleProtocolEnum(str, Enum):
    """Firewall rule protocol enum."""

    TCP = "tcp"
    UDP = "udp"


@dataclass
class FirewallRule:
    """Domain entity representing a firewall rule."""

    policy_id: int
    order_index: int
    id: int | None = None
    source_cidr: str | None = None
    destination_cidr: str | None = None
    protocol: RuleProtocolEnum = RuleProtocolEnum.TCP
    source_port_minimum: int | None = None
    source_port_maximum: int | None = None
    destination_port_minimum: int | None = None
    destination_port_maximum: int | None = None
    action: RuleActionEnum = RuleActionEnum.ALLOW
