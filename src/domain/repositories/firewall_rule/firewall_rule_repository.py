from abc import ABC, abstractmethod

from src.domain.entities.firewall_rule.firewall_rule import FirewallRule
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class FirewallRuleRepository(ABC):
    """Abstract repository for FirewallRule entities."""

    @abstractmethod
    def create(self, rule: FirewallRule) -> FirewallRule:
        """Create a new firewall rule."""

    @abstractmethod
    def get_paginated(
        self, firewall_id: int, policy_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Get all firewall rules."""

    @abstractmethod
    def get_by_firewall_id_and_policy_id(
        self, firewall_id: int, policy_id: int, rule_id: int
    ) -> FirewallRule | None:
        """Get all rules for a specific policy."""

    @abstractmethod
    def delete(self, rule_id: int) -> bool:
        """Delete a firewall rule by ID."""
