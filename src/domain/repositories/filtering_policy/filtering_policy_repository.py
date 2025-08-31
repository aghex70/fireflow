from abc import ABC, abstractmethod

from src.domain.entities.filtering_policy.filtering_policy import FilteringPolicy
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class FilteringPolicyRepository(ABC):
    """Abstract repository for FilteringPolicy entities."""

    @abstractmethod
    def create(self, policy: FilteringPolicy) -> FilteringPolicy:
        """Create a new filtering policy."""

    @abstractmethod
    def get_by_id_and_firewall_id(
        self, policy_id: int, firewall_id: int
    ) -> FilteringPolicy | None:
        """Get filtering policy by ID and firewall ID."""

    @abstractmethod
    def get_paginated(
        self, firewall_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Get all filtering policies."""

    @abstractmethod
    def delete(self, policy_id: int) -> bool:
        """Delete a filtering policy by ID."""
