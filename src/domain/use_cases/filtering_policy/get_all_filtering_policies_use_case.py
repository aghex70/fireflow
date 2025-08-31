"""Get all filtering policies use case."""

from src.domain.services.filtering_policy.service import FilteringPolicyService
from src.domain.services.firewall.service import FirewallService
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class GetAllFilteringPoliciesUseCase:
    """Use case for retrieving all filtering policies."""

    def __init__(
        self, filtering_policy_service: FilteringPolicyService, firewall_service: FirewallService
    ):
        self.filtering_policy_service = filtering_policy_service
        self.firewall_service = firewall_service

    def execute(
        self, firewall_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Execute the get all filtering policies use case."""
        return self.filtering_policy_service.get_all_filtering_policies(
            firewall_id=firewall_id, pagination=pagination
        )
