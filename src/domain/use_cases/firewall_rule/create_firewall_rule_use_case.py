"""Create firewall rule use case."""

from src.domain.entities.firewall_rule.firewall_rule import FirewallRule
from src.domain.services.filtering_policy.service import FilteringPolicyService
from src.domain.services.firewall_rule.service import FirewallRuleService
from src.infrastructure.web.schemas.firewall_rule.firewall_rule_schemas import (
    FirewallRuleCreateSchema,
)


class CreateFirewallRuleUseCase:
    """Use case for creating a new firewall rule."""

    def __init__(
        self,
        filtering_policy_service: FilteringPolicyService,
        firewall_rule_service: FirewallRuleService,
    ):
        self.firewall_rule_service = firewall_rule_service
        self.filtering_policy_service = filtering_policy_service

    def execute(
        self,
        firewall_id: int,
        policy_id: int,
        schema: FirewallRuleCreateSchema,
    ) -> FirewallRule:
        """Execute the create firewall rule use case."""

        # Check first if the firewall policy exists
        policy = self.filtering_policy_service.get_filtering_policy_by_id(
            policy_id, firewall_id
        )
        if not policy:
            raise ValueError(
                f"Filtering policy with firewall id {firewall_id} and policy id {policy_id} not found"
            )

        # Create new rule
        rule = FirewallRule(
            policy_id=policy_id,
            order_index=schema.order_index,
            source_cidr=schema.source_cidr,
            destination_cidr=schema.destination_cidr,
            protocol=schema.protocol,
            source_port_minimum=schema.source_port_minimum,
            source_port_maximum=schema.source_port_maximum,
            destination_port_minimum=schema.destination_port_minimum,
            destination_port_maximum=schema.destination_port_maximum,
            action=schema.action,
        )

        return self.firewall_rule_service.create_firewall_rule(rule)
