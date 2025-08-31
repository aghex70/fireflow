"""Delete firewall rule use case."""

from src.domain.services.firewall_rule.service import FirewallRuleService


class DeleteFirewallRuleUseCase:
    """Use case for deleting a firewall rule."""

    def __init__(self, rule_service: FirewallRuleService):
        self.rule_service = rule_service

    def execute(self, firewall_id: int, policy_id: int, rule_id: int) -> bool:
        """Execute the delete firewall rule use case."""
        # Check if rule exists
        rule = self.rule_service.get_by_firewall_id_and_policy_id(
            firewall_id, policy_id, rule_id
        )
        if not rule:
            raise ValueError(
                f"Firewall rule with firewall id {firewall_id} and policy id {policy_id} and rule id {rule_id} not found"
            )

        return self.rule_service.delete_firewall_rule(rule_id)
