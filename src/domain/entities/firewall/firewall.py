from dataclasses import dataclass
from enum import Enum


class FirewallEnvironmentEnum(str, Enum):
    """Firewall environment enum."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


@dataclass
class Firewall:
    """Domain entity representing a firewall."""

    name: str
    environment: FirewallEnvironmentEnum
    scope: str
    id: int | None = None
    description: str | None = None
