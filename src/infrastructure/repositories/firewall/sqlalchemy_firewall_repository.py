import logging

from sqlalchemy.orm import Session, joinedload

from src.domain.entities.firewall.firewall import Firewall
from src.domain.repositories.firewall.firewall_repository import FirewallRepository
from src.infrastructure.database.models import SQLFirewall
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
    paginate_query,
)


logger = logging.getLogger(__name__)


class SQLAlchemyFirewallRepository(FirewallRepository):
    """SQLAlchemy implementation of FirewallRepository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, firewall: Firewall) -> Firewall:
        """Create a new firewall."""
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        self.session.add(db_firewall)
        self.session.flush()

        return self._to_entity(db_firewall)

    def get_by_id(self, firewall_id: int) -> Firewall | None:
        """Get firewall by ID with optimized loading."""
        db_firewall = (
            self.session.query(SQLFirewall)
            .options(joinedload(SQLFirewall.policies))
            .filter(SQLFirewall.id == firewall_id)
            .first()
        )

        return self._to_entity(db_firewall) if db_firewall else None

    def get_paginated(
        self,
        pagination: PaginationRequest,
    ) -> PaginationResponse:
        """Get paginated firewalls with filtering and search."""
        query = self.session.query(SQLFirewall).options(
            joinedload(SQLFirewall.policies)
        )

        # Define sortable columns
        sort_columns = {
            "id": SQLFirewall.id,
            "name": SQLFirewall.name,
            "environment": SQLFirewall.environment,
            "scope": SQLFirewall.scope,
            "created_at": SQLFirewall.created_at,
            "updated_at": SQLFirewall.updated_at,
        }

        # Paginate
        paginated_result = paginate_query(query, pagination, sort_columns)

        # Convert items to entities
        paginated_result.items = [self._to_entity(fw) for fw in paginated_result.items]

        return paginated_result

    def delete(self, firewall_id: int) -> bool:
        """Delete a firewall by ID."""
        db_firewall = (
            self.session.query(SQLFirewall)
            .filter(SQLFirewall.id == firewall_id)
            .first()
        )

        if db_firewall:
            self.session.delete(db_firewall)
            return True
        return False

    def get_by_name(self, name: str) -> Firewall | None:
        """Get firewall by name."""
        db_firewall = (
            self.session.query(SQLFirewall).filter(SQLFirewall.name == name).first()
        )

        return self._to_entity(db_firewall) if db_firewall else None

    def _to_entity(self, db_firewall: SQLFirewall) -> Firewall:
        """Convert database model to domain entity."""
        return Firewall(
            id=db_firewall.id,
            name=db_firewall.name,
            description=db_firewall.description,
            environment=db_firewall.environment,
            scope=db_firewall.scope,
        )
