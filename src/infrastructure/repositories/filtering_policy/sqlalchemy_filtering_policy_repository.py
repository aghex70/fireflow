from sqlalchemy.orm import Session, joinedload

from src.domain.entities.filtering_policy.filtering_policy import (
    FilteringPolicy,
    PolicyActionEnum,
    PolicyStatusEnum,
)
from src.domain.repositories.filtering_policy.filtering_policy_repository import (
    FilteringPolicyRepository,
)
from src.infrastructure.database.models import (
    SQLFilteringPolicy,
)
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
    paginate_query,
)


class SQLAlchemyFilteringPolicyRepository(FilteringPolicyRepository):
    """SQLAlchemy implementation of FilteringPolicyRepository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, policy: FilteringPolicy) -> FilteringPolicy:
        """Create a new filtering policy."""
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        self.session.add(db_policy)
        self.session.flush()

        return self._to_entity(db_policy)

    def get_by_id_and_firewall_id(
        self, policy_id: int, firewall_id: int
    ) -> FilteringPolicy | None:
        """Get filtering policy by ID with optimized loading."""
        db_policy = (
            self.session.query(SQLFilteringPolicy)
            .options(
                joinedload(SQLFilteringPolicy.firewall),
                joinedload(SQLFilteringPolicy.rules),
            )
            .filter(
                SQLFilteringPolicy.id == policy_id,
                SQLFilteringPolicy.firewall_id == firewall_id,
            )
            .first()
        )

        return self._to_entity(db_policy) if db_policy else None

    def get_paginated(
        self,
        firewall_id: int,
        pagination: PaginationRequest,
    ) -> PaginationResponse:
        """Get paginated policies."""
        query = (
            self.session.query(SQLFilteringPolicy)
            .filter(SQLFilteringPolicy.firewall_id == firewall_id)
            .options(
                joinedload(SQLFilteringPolicy.firewall),
                joinedload(SQLFilteringPolicy.rules),
            )
        )

        # Define sortable columns
        sort_columns = {
            "id": SQLFilteringPolicy.id,
            "name": SQLFilteringPolicy.name,
            "priority": SQLFilteringPolicy.priority,
            "action": SQLFilteringPolicy.action,
            "status": SQLFilteringPolicy.status,
            "firewall_id": SQLFilteringPolicy.firewall_id,
            "created_at": SQLFilteringPolicy.created_at,
            "updated_at": SQLFilteringPolicy.updated_at,
        }

        # Paginate
        paginated_result = paginate_query(query, pagination, sort_columns)

        # Convert items to entities
        paginated_result.items = [
            self._to_entity(policy) for policy in paginated_result.items
        ]

        return paginated_result

    def delete(self, policy_id: int) -> bool:
        """Delete a filtering policy by ID."""
        db_policy = (
            self.session.query(SQLFilteringPolicy)
            .filter(SQLFilteringPolicy.id == policy_id)
            .first()
        )

        if db_policy:
            self.session.delete(db_policy)
            return True
        return False

    def _to_entity(self, db_policy: SQLFilteringPolicy) -> FilteringPolicy:
        """Convert database model to domain entity."""
        return FilteringPolicy(
            id=db_policy.id,
            firewall_id=db_policy.firewall_id,
            name=db_policy.name,
            description=db_policy.description,
            priority=db_policy.priority,
            action=PolicyActionEnum(db_policy.action),
            status=PolicyStatusEnum(db_policy.status),
        )
