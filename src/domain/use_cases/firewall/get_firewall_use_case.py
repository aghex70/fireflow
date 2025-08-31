"""Get firewall use case."""

from src.domain.entities.firewall.firewall import Firewall
from src.domain.services.firewall.service import FirewallService


class GetFirewallUseCase:
    """Use case for retrieving a firewall."""

    def __init__(self, firewall_service: FirewallService):
        self.firewall_service = firewall_service

    def execute(self, firewall_id: int) -> Firewall:
        """Execute the get firewall use case."""
        firewall = self.firewall_service.get_firewall_by_id(firewall_id)
        if not firewall:
            raise ValueError(f"Firewall with id {firewall_id} not found")
        return firewall
