from abc import ABC, abstractmethod

from src.domain.entities.firewall.firewall import Firewall
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class FirewallRepository(ABC):
    """Abstract repository for Firewall entities."""

    @abstractmethod
    def create(self, firewall: Firewall) -> Firewall:
        """Create a new firewall."""

    @abstractmethod
    def get_by_id(self, firewall_id: int) -> Firewall | None:
        """Get firewall by ID."""

    @abstractmethod
    def get_paginated(self, pagination: PaginationRequest) -> PaginationResponse:
        """Get all firewalls."""

    @abstractmethod
    def delete(self, firewall_id: int) -> bool:
        """Delete a firewall by ID."""

    @abstractmethod
    def get_by_name(self, name: str) -> Firewall | None:
        """Get firewall by name."""
