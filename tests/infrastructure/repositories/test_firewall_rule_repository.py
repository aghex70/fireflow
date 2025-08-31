"""Tests for FirewallRule repository."""

import pytest

from src.domain.entities.firewall_rule.firewall_rule import (
    FirewallRule,
    RuleActionEnum,
    RuleProtocolEnum,
)
from src.infrastructure.database.models import (
    SQLFilteringPolicy,
    SQLFirewall,
    SQLFirewallRule,
)
from src.infrastructure.repositories.firewall_rule.sqlalchemy_firewall_rule_repository import (
    SQLAlchemyFirewallRuleRepository,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from tests.factories.filtering_policy_factories import FilteringPolicyFactory
from tests.factories.firewall_factories import FirewallFactory
from tests.factories.firewall_rule_factories import FirewallRuleFactory


class TestSQLAlchemyFirewallRuleRepository:
    """Test cases for SQLAlchemy FirewallRule repository."""

    def test_create_rule_success(self, db_session):
        """Test successful firewall rule creation."""
        # Arrange
        # Create firewall and policy first
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)

        # Act
        created_rule = repository.create(rule)

        # Assert
        assert created_rule.id is not None
        assert created_rule.policy_id == rule.policy_id
        assert created_rule.order_index == rule.order_index
        assert created_rule.source_cidr == rule.source_cidr
        assert created_rule.destination_cidr == rule.destination_cidr
        assert created_rule.protocol == rule.protocol
        assert created_rule.action == rule.action

        # Verify in database
        db_rule = db_session.query(SQLFirewallRule).filter_by(id=created_rule.id).first()
        assert db_rule is not None
        assert db_rule.policy_id == rule.policy_id

    def test_get_by_firewall_id_and_policy_id_existing_rule(self, db_session):
        """Test getting rule by existing IDs."""
        # Arrange
        # Create firewall and policy first
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        created_rule = repository.create(rule)
        db_session.commit()

        # Act
        found_rule = repository.get_by_firewall_id_and_policy_id(
            db_firewall.id, db_policy.id, created_rule.id
        )

        # Assert
        assert found_rule is not None
        assert found_rule.id == created_rule.id
        assert found_rule.policy_id == db_policy.id

    def test_get_by_firewall_id_and_policy_id_nonexistent_rule_returns_none(self, db_session):
        """Test getting rule by non-existent ID returns None."""
        # Arrange
        repository = SQLAlchemyFirewallRuleRepository(db_session)

        # Act
        found_rule = repository.get_by_firewall_id_and_policy_id(99999, 99999, 99999)

        # Assert
        assert found_rule is None

    def test_get_by_firewall_id_and_policy_id_wrong_firewall_returns_none(self, db_session):
        """Test getting rule with wrong firewall ID returns None."""
        # Arrange
        # Create two firewalls with policies
        firewall1 = FirewallFactory.build()
        db_firewall1 = SQLFirewall(
            name=firewall1.name,
            description=firewall1.description,
            environment=firewall1.environment,
            scope=firewall1.scope,
        )
        db_session.add(db_firewall1)

        firewall2 = FirewallFactory.build()
        db_firewall2 = SQLFirewall(
            name=firewall2.name,
            description=firewall2.description,
            environment=firewall2.environment,
            scope=firewall2.scope,
        )
        db_session.add(db_firewall2)
        db_session.flush()

        # Create policy for firewall1
        policy1 = FilteringPolicyFactory.build(firewall_id=db_firewall1.id)
        db_policy1 = SQLFilteringPolicy(
            firewall_id=policy1.firewall_id,
            name=policy1.name,
            description=policy1.description,
            priority=policy1.priority,
            action=policy1.action.value,
            status=policy1.status.value,
        )
        db_session.add(db_policy1)
        db_session.flush()

        # Create rule for policy1
        rule = FirewallRuleFactory.build(policy_id=db_policy1.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        created_rule = repository.create(rule)
        db_session.commit()

        # Act - try to get rule with wrong firewall ID
        found_rule = repository.get_by_firewall_id_and_policy_id(
            db_firewall2.id, db_policy1.id, created_rule.id
        )

        # Assert
        assert found_rule is None

    def test_delete_existing_rule_success(self, db_session):
        """Test successful deletion of existing rule."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        created_rule = repository.create(rule)
        db_session.commit()

        # Act
        result = repository.delete(created_rule.id)

        # Assert
        assert result is True
        
        # Verify rule is deleted from database
        db_rule = db_session.query(SQLFirewallRule).filter_by(id=created_rule.id).first()
        assert db_rule is None

    def test_delete_nonexistent_rule_returns_false(self, db_session):
        """Test deletion of non-existent rule returns False."""
        # Arrange
        repository = SQLAlchemyFirewallRuleRepository(db_session)

        # Act
        result = repository.delete(99999)

        # Assert
        assert result is False

    def test_get_paginated_empty_results(self, db_session):
        """Test getting paginated rules when none exist."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        repository = SQLAlchemyFirewallRuleRepository(db_session)
        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(db_firewall.id, db_policy.id, pagination)

        # Assert
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 0

    def test_get_paginated_multiple_rules(self, db_session):
        """Test getting paginated rules with multiple results."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rules = FirewallRuleFactory.batch(5, policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        
        for rule in rules:
            repository.create(rule)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(db_firewall.id, db_policy.id, pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 1

        # Verify all rules are returned as entities
        for item in result.items:
            assert isinstance(item, FirewallRule)
            assert item.policy_id == db_policy.id

    def test_get_paginated_with_pagination_limits(self, db_session):
        """Test paginated results respect pagination limits."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rules = FirewallRuleFactory.batch(15, policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        
        for rule in rules:
            repository.create(rule)
        db_session.commit()

        pagination = PaginationRequest(page=2, size=5)

        # Act
        result = repository.get_paginated(db_firewall.id, db_policy.id, pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 15
        assert result.page == 2
        assert result.size == 5
        assert result.total_pages == 3

    def test_get_paginated_with_sorting_by_order_index(self, db_session):
        """Test paginated results with sorting by order_index."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule1 = FirewallRuleFactory.build(policy_id=db_policy.id, order_index=30)
        rule2 = FirewallRuleFactory.build(policy_id=db_policy.id, order_index=10)
        rule3 = FirewallRuleFactory.build(policy_id=db_policy.id, order_index=20)
        
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        repository.create(rule1)
        repository.create(rule2)
        repository.create(rule3)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10, sort_by="order_index", sort_dir="asc")

        # Act
        result = repository.get_paginated(db_firewall.id, db_policy.id, pagination)

        # Assert
        assert len(result.items) == 3
        assert result.items[0].order_index == 10
        assert result.items[1].order_index == 20
        assert result.items[2].order_index == 30

    def test_to_entity_conversion(self, db_session):
        """Test conversion from database model to domain entity."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id)
        repository = SQLAlchemyFirewallRuleRepository(db_session)
        
        # Create rule to get database model
        created_rule = repository.create(rule)
        db_session.commit()
        
        db_rule = db_session.query(SQLFirewallRule).filter_by(id=created_rule.id).first()

        # Act
        entity = repository._to_entity(db_rule)

        # Assert
        assert isinstance(entity, FirewallRule)
        assert entity.id == db_rule.id
        assert entity.policy_id == db_rule.policy_id
        assert entity.order_index == db_rule.order_index
        assert entity.source_cidr == db_rule.source_cidr
        assert entity.destination_cidr == db_rule.destination_cidr
        assert entity.protocol == RuleProtocolEnum(db_rule.protocol)
        assert entity.action == RuleActionEnum(db_rule.action)

    @pytest.mark.parametrize("protocol", [
        RuleProtocolEnum.TCP,
        RuleProtocolEnum.UDP
    ])
    def test_create_rule_with_different_protocols(self, db_session, protocol):
        """Test creating rules with different protocols."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id, protocol=protocol)
        repository = SQLAlchemyFirewallRuleRepository(db_session)

        # Act
        created_rule = repository.create(rule)

        # Assert
        assert created_rule.protocol == protocol
        
        # Verify in database
        db_rule = db_session.query(SQLFirewallRule).filter_by(id=created_rule.id).first()
        assert db_rule.protocol == protocol.value

    @pytest.mark.parametrize("action", [RuleActionEnum.ALLOW, RuleActionEnum.DENY])
    def test_create_rule_with_different_actions(self, db_session, action):
        """Test creating rules with different actions."""
        # Arrange
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id)
        db_policy = SQLFilteringPolicy(
            firewall_id=policy.firewall_id,
            name=policy.name,
            description=policy.description,
            priority=policy.priority,
            action=policy.action.value,
            status=policy.status.value,
        )
        db_session.add(db_policy)
        db_session.flush()

        rule = FirewallRuleFactory.build(policy_id=db_policy.id, action=action)
        repository = SQLAlchemyFirewallRuleRepository(db_session)

        # Act
        created_rule = repository.create(rule)

        # Assert
        assert created_rule.action == action
        
        # Verify in database
        db_rule = db_session.query(SQLFirewallRule).filter_by(id=created_rule.id).first()
        assert db_rule.action == action.value