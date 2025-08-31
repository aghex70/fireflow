"""Create filtering policy use case."""

import logging

from src.domain.entities.filtering_policy.filtering_policy import FilteringPolicy
from src.domain.services.filtering_policy.service import FilteringPolicyService
from src.domain.services.firewall.service import FirewallService
from src.infrastructure.web.schemas.filtering_policy.filtering_policy_schemas import (
    FilteringPolicyCreateSchema,
)


logger = logging.getLogger(__name__)


class CreateFilteringPolicyUseCase:
    """Use case for creating a new filtering policy."""

    def __init__(
        self,
        filtering_policy_service: FilteringPolicyService,
        firewall_service: FirewallService,
    ):
        self.filtering_policy_service = filtering_policy_service
        self.firewall_service = firewall_service

    def execute(
        self,
        firewall_id: int,
        schema: FilteringPolicyCreateSchema,
    ) -> FilteringPolicy:
        """Execute the create filtering policy use case."""

        # Validate firewall exists
        firewall = self.firewall_service.get_firewall_by_id(firewall_id)
        if not firewall:
            raise ValueError(f"Firewall with id {firewall_id} not found")

        # Create new policy
        policy = FilteringPolicy(
            firewall_id=firewall_id,
            name=schema.name,
            description=schema.description,
            priority=schema.priority,
            action=schema.action,
            status=schema.status,
        )

        return self.filtering_policy_service.create_filtering_policy(policy)
