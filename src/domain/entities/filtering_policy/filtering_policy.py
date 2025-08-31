from dataclasses import dataclass
from enum import Enum


class PolicyActionEnum(str, Enum):
    """Filtering policy action enum."""

    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"


class PolicyStatusEnum(str, Enum):
    """Filtering policy status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class FilteringPolicy:
    """Domain entity representing a filtering policy."""

    firewall_id: int
    name: str
    priority: int
    action: PolicyActionEnum = PolicyActionEnum.ALLOW
    status: PolicyStatusEnum = PolicyStatusEnum.ACTIVE
    id: int | None = None
    description: str | None = None
