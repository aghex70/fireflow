import logging

from src.domain.entities.firewall.firewall import Firewall
from src.domain.repositories.firewall.firewall_repository import FirewallRepository
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


logger = logging.getLogger(__name__)


class FirewallService:
    """Service class for managing firewall-related operations."""

    def __init__(self, repository: FirewallRepository):
        self.repository = repository

    def create_firewall(self, firewall: Firewall) -> Firewall:
        """Create a new firewall."""
        return self.repository.create(firewall)

    def get_firewall_by_id(self, firewall_id: int) -> Firewall | None:
        """Get firewall by ID."""
        return self.repository.get_by_id(firewall_id)

    def get_firewall_by_name(self, name: str) -> Firewall | None:
        """Get firewall by name."""
        return self.repository.get_by_name(name)

    def get_all_firewalls(self, pagination: PaginationRequest) -> PaginationResponse:
        """Get all firewalls."""
        return self.repository.get_paginated(pagination=pagination)

    def delete_firewall(self, firewall_id: int) -> bool:
        """Delete a firewall by ID."""
        return self.repository.delete(firewall_id)
