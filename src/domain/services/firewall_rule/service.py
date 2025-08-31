import logging

from src.domain.entities.firewall_rule.firewall_rule import FirewallRule
from src.domain.repositories.firewall_rule.firewall_rule_repository import (
    FirewallRuleRepository,
)
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


logger = logging.getLogger(__name__)


class FirewallRuleService:
    """Service class for managing firewall rule-related operations."""

    def __init__(self, repository: FirewallRuleRepository):
        self.repository = repository

    def create_firewall_rule(self, rule: FirewallRule) -> FirewallRule:
        """Create a new firewall rule."""
        return self.repository.create(rule)

    def get_all_firewall_rules(
        self, firewall_id: int, policy_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Get all firewall rules."""
        return self.repository.get_paginated(
            firewall_id=firewall_id, policy_id=policy_id, pagination=pagination
        )

    def get_by_firewall_id_and_policy_id(
        self, firewall_id: int, policy_id: int, rule_id: int
    ) -> FirewallRule | None:
        """Get a firewall rule by firewall ID and policy ID."""
        return self.repository.get_by_firewall_id_and_policy_id(
            firewall_id, policy_id, rule_id
        )

    def delete_firewall_rule(self, rule_id: int) -> bool:
        """Delete a firewall rule by ID."""
        return self.repository.delete(rule_id)
