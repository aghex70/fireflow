"""Get all firewalls use case."""

from src.domain.services.firewall.service import FirewallService
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class GetAllFirewallsUseCase:
    """Use case for retrieving all firewalls."""

    def __init__(self, firewall_service: FirewallService):
        self.firewall_service = firewall_service

    def execute(self, pagination: PaginationRequest) -> PaginationResponse:
        """Execute the get all firewalls use case."""
        return self.firewall_service.get_all_firewalls(pagination)
