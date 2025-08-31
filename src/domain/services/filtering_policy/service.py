import logging

from src.domain.entities.filtering_policy.filtering_policy import FilteringPolicy
from src.domain.repositories.filtering_policy.filtering_policy_repository import (
    FilteringPolicyRepository,
)
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


logger = logging.getLogger(__name__)


class FilteringPolicyService:
    """Service class for managing filtering policy-related operations."""

    def __init__(self, repository: FilteringPolicyRepository):
        self.repository = repository

    def create_filtering_policy(self, policy: FilteringPolicy) -> FilteringPolicy:
        """Create a new filtering policy."""
        return self.repository.create(policy)

    def get_filtering_policy_by_id(
        self, policy_id: int, firewall_id: int
    ) -> FilteringPolicy | None:
        """Get filtering policy by ID and firewall ID."""
        return self.repository.get_by_id_and_firewall_id(policy_id, firewall_id)

    def get_all_filtering_policies(
        self, firewall_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Get all filtering policies."""
        return self.repository.get_paginated(
            firewall_id=firewall_id, pagination=pagination
        )

    def delete_filtering_policy(self, policy_id: int) -> bool:
        """Delete a filtering policy by ID."""
        return self.repository.delete(policy_id)
