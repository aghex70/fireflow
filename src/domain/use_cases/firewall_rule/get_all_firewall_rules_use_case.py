"""Get all firewall rules use case."""

from src.domain.services.firewall_rule.service import FirewallRuleService
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class GetAllFirewallRulesUseCase:
    """Use case for retrieving all firewall rules."""

    def __init__(self, firewall_rule_service: FirewallRuleService):
        self.firewall_rule_service = firewall_rule_service

    def execute(
        self, firewall_id: int, policy_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Execute the get all firewall rules use case."""
        return self.firewall_rule_service.get_all_firewall_rules(
            firewall_id, policy_id, pagination
        )
