from sqlalchemy.orm import Session, joinedload

from src.domain.entities.firewall_rule.firewall_rule import (
    FirewallRule,
    RuleActionEnum,
    RuleProtocolEnum,
)
from src.domain.repositories.firewall_rule.firewall_rule_repository import (
    FirewallRuleRepository,
)
from src.infrastructure.database.models import (
    SQLFilteringPolicy,
    SQLFirewall,
    SQLFirewallRule,
)
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
    paginate_query,
)


class SQLAlchemyFirewallRuleRepository(FirewallRuleRepository):
    """SQLAlchemy implementation of FirewallRuleRepository."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, rule: FirewallRule) -> FirewallRule:
        """Create a new firewall rule."""
        db_rule = SQLFirewallRule(
            policy_id=rule.policy_id,
            order_index=rule.order_index,
            source_cidr=rule.source_cidr,
            destination_cidr=rule.destination_cidr,
            protocol=rule.protocol.value,
            source_port_minimum=rule.source_port_minimum,
            source_port_maximum=rule.source_port_maximum,
            destination_port_minimum=rule.destination_port_minimum,
            destination_port_maximum=rule.destination_port_maximum,
            action=rule.action.value,
        )
        self.session.add(db_rule)
        self.session.flush()

        return self._to_entity(db_rule)

    def get_paginated(
        self, firewall_id: int, policy_id: int, pagination: PaginationRequest
    ) -> PaginationResponse:
        """Get paginated firewall rules."""
        query = (
            self.session.query(SQLFirewallRule)
            .join(SQLFilteringPolicy)
            .join(SQLFirewall)
            .options(
                joinedload(SQLFirewallRule.policy).joinedload(
                    SQLFilteringPolicy.firewall
                )
            )
            .filter(
                SQLFirewallRule.policy_id == policy_id,
                SQLFilteringPolicy.firewall_id == firewall_id,
            )
        )

        sort_columns = {
            "id": SQLFirewallRule.id,
            "order_index": SQLFirewallRule.order_index,
            "source_cidr": SQLFirewallRule.source_cidr,
            "destination_cidr": SQLFirewallRule.destination_cidr,
            "protocol": SQLFirewallRule.protocol,
        }

        # Paginate
        paginated_result = paginate_query(query, pagination, sort_columns)

        # Convert items to entities
        paginated_result.items = [
            self._to_entity(rule) for rule in paginated_result.items
        ]

        return paginated_result

    def get_by_firewall_id_and_policy_id(
        self, firewall_id: int, policy_id: int, rule_id: int
    ) -> FirewallRule | None:
        """Get rule for a specific policy."""
        rule = (
            self.session.query(SQLFirewallRule)
            .join(SQLFilteringPolicy)
            .join(SQLFirewall)
            .filter(
                SQLFirewallRule.policy_id == SQLFilteringPolicy.id,
                SQLFilteringPolicy.firewall_id == SQLFirewall.id,
                SQLFirewallRule.policy_id == policy_id,
                SQLFilteringPolicy.firewall_id == firewall_id,
                SQLFirewallRule.id == rule_id,
            )
            .first()
        )

        return self._to_entity(rule) if rule else None

    def delete(self, rule_id: int) -> bool:
        """Delete a firewall rule by ID."""
        db_rule = (
            self.session.query(SQLFirewallRule)
            .filter(SQLFirewallRule.id == rule_id)
            .first()
        )

        if db_rule:
            self.session.delete(db_rule)
            return True
        return False

    def _to_entity(self, db_rule: SQLFirewallRule) -> FirewallRule:
        """Convert database model to domain entity."""
        return FirewallRule(
            id=db_rule.id,
            policy_id=db_rule.policy_id,
            order_index=db_rule.order_index,
            source_cidr=db_rule.source_cidr,
            destination_cidr=db_rule.destination_cidr,
            protocol=RuleProtocolEnum(db_rule.protocol),
            source_port_minimum=db_rule.source_port_minimum,
            source_port_maximum=db_rule.source_port_maximum,
            destination_port_minimum=db_rule.destination_port_minimum,
            destination_port_maximum=db_rule.destination_port_maximum,
            action=RuleActionEnum(db_rule.action),
        )
