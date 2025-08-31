"""Create firewall use case."""

import logging

from src.domain.entities.firewall.firewall import Firewall
from src.domain.services.firewall.service import FirewallService
from src.infrastructure.web.schemas.firewall.firewall_schemas import (
    FirewallCreateSchema,
)


logger = logging.getLogger(__name__)


class CreateFirewallUseCase:
    """Use case for creating a new firewall."""

    def __init__(self, firewall_service: FirewallService):
        self.firewall_service = firewall_service

    def execute(
        self,
        schema: FirewallCreateSchema,
    ) -> Firewall:
        """Execute the create firewall use case."""
        # Check if firewall with same name already exists
        existing_firewall = self.firewall_service.get_firewall_by_name(schema.name)
        if existing_firewall:
            raise ValueError(f"Firewall with name '{schema.name}' already exists")

        # Create new firewall
        firewall = Firewall(
            name=schema.name,
            description=schema.description,
            environment=schema.environment,
            scope=schema.scope,
        )

        return self.firewall_service.create_firewall(firewall)
