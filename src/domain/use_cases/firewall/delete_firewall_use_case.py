"""Delete firewall use case."""

from src.domain.services.firewall.service import FirewallService


class DeleteFirewallUseCase:
    """Use case for deleting a firewall."""

    def __init__(self, firewall_service: FirewallService):
        self.firewall_service = firewall_service

    def execute(self, firewall_id: int) -> bool:
        """Execute the delete firewall use case."""
        # Check if firewall exists
        firewall = self.firewall_service.get_firewall_by_id(firewall_id)
        if not firewall:
            raise ValueError(f"Firewall with id {firewall_id} not found")

        return self.firewall_service.delete_firewall(firewall_id)
