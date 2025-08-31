"""Tests for FilteringPolicy repository."""

import pytest

from src.domain.entities.filtering_policy.filtering_policy import (
    FilteringPolicy,
    PolicyActionEnum,
    PolicyStatusEnum,
)
from src.infrastructure.database.models import SQLFilteringPolicy, SQLFirewall
from src.infrastructure.repositories.filtering_policy.sqlalchemy_filtering_policy_repository import (
    SQLAlchemyFilteringPolicyRepository,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from tests.factories.filtering_policy_factories import FilteringPolicyFactory
from tests.factories.firewall_factories import FirewallFactory


class TestSQLAlchemyFilteringPolicyRepository:
    """Test cases for SQLAlchemy FilteringPolicy repository."""

    def test_create_policy_success(self, db_session):
        """Test successful filtering policy creation."""
        # Arrange
        # Create a firewall first
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
        repository = SQLAlchemyFilteringPolicyRepository(db_session)

        # Act
        created_policy = repository.create(policy)

        # Assert
        assert created_policy.id is not None
        assert created_policy.firewall_id == policy.firewall_id
        assert created_policy.name == policy.name
        assert created_policy.description == policy.description
        assert created_policy.priority == policy.priority
        assert created_policy.action == policy.action
        assert created_policy.status == policy.status

        # Verify in database
        db_policy = db_session.query(SQLFilteringPolicy).filter_by(id=created_policy.id).first()
        assert db_policy is not None
        assert db_policy.name == policy.name

    def test_get_by_id_and_firewall_id_existing_policy(self, db_session):
        """Test getting policy by existing ID and firewall ID."""
        # Arrange
        # Create a firewall first
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
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        created_policy = repository.create(policy)
        db_session.commit()

        # Act
        found_policy = repository.get_by_id_and_firewall_id(created_policy.id, db_firewall.id)

        # Assert
        assert found_policy is not None
        assert found_policy.id == created_policy.id
        assert found_policy.firewall_id == db_firewall.id
        assert found_policy.name == policy.name

    def test_get_by_id_and_firewall_id_nonexistent_policy_returns_none(self, db_session):
        """Test getting policy by non-existent ID returns None."""
        # Arrange
        repository = SQLAlchemyFilteringPolicyRepository(db_session)

        # Act
        found_policy = repository.get_by_id_and_firewall_id(99999, 99999)

        # Assert
        assert found_policy is None

    def test_get_by_id_and_firewall_id_wrong_firewall_returns_none(self, db_session):
        """Test getting policy with wrong firewall ID returns None."""
        # Arrange
        # Create two firewalls
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
        policy = FilteringPolicyFactory.build(firewall_id=db_firewall1.id)
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        created_policy = repository.create(policy)
        db_session.commit()

        # Act - try to get policy with wrong firewall ID
        found_policy = repository.get_by_id_and_firewall_id(created_policy.id, db_firewall2.id)

        # Assert
        assert found_policy is None

    def test_delete_existing_policy_success(self, db_session):
        """Test successful deletion of existing policy."""
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
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        created_policy = repository.create(policy)
        db_session.commit()

        # Act
        result = repository.delete(created_policy.id)

        # Assert
        assert result is True
        
        # Verify policy is deleted from database
        db_policy = db_session.query(SQLFilteringPolicy).filter_by(id=created_policy.id).first()
        assert db_policy is None

    def test_delete_nonexistent_policy_returns_false(self, db_session):
        """Test deletion of non-existent policy returns False."""
        # Arrange
        repository = SQLAlchemyFilteringPolicyRepository(db_session)

        # Act
        result = repository.delete(99999)

        # Assert
        assert result is False

    def test_get_paginated_empty_results(self, db_session):
        """Test getting paginated policies when none exist."""
        # Arrange
        # Create a firewall first
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(db_firewall.id, pagination)

        # Assert
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 0

    def test_get_paginated_multiple_policies(self, db_session):
        """Test getting paginated policies with multiple results."""
        # Arrange
        # Create a firewall first
        firewall = FirewallFactory.build()
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        db_session.add(db_firewall)
        db_session.flush()

        policies = FilteringPolicyFactory.batch(5, firewall_id=db_firewall.id)
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        
        for policy in policies:
            repository.create(policy)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(db_firewall.id, pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 1

        # Verify all policies are returned as entities
        for item in result.items:
            assert isinstance(item, FilteringPolicy)
            assert item.firewall_id == db_firewall.id

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

        policies = FilteringPolicyFactory.batch(15, firewall_id=db_firewall.id)
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        
        for policy in policies:
            repository.create(policy)
        db_session.commit()

        pagination = PaginationRequest(page=2, size=5)

        # Act
        result = repository.get_paginated(db_firewall.id, pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 15
        assert result.page == 2
        assert result.size == 5
        assert result.total_pages == 3

    def test_get_paginated_with_sorting_by_priority(self, db_session):
        """Test paginated results with sorting by priority."""
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

        policy1 = FilteringPolicyFactory.build(firewall_id=db_firewall.id, priority=300)
        policy2 = FilteringPolicyFactory.build(firewall_id=db_firewall.id, priority=100)
        policy3 = FilteringPolicyFactory.build(firewall_id=db_firewall.id, priority=200)
        
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        repository.create(policy1)
        repository.create(policy2)
        repository.create(policy3)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10, sort_by="priority", sort_dir="asc")

        # Act
        result = repository.get_paginated(db_firewall.id, pagination)

        # Assert
        assert len(result.items) == 3
        assert result.items[0].priority == 100
        assert result.items[1].priority == 200
        assert result.items[2].priority == 300

    def test_get_paginated_filters_by_firewall_id(self, db_session):
        """Test that paginated results are filtered by firewall ID."""
        # Arrange
        # Create two firewalls
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

        # Create policies for both firewalls
        policies_fw1 = FilteringPolicyFactory.batch(3, firewall_id=db_firewall1.id)
        policies_fw2 = FilteringPolicyFactory.batch(2, firewall_id=db_firewall2.id)
        
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        
        for policy in policies_fw1 + policies_fw2:
            repository.create(policy)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10)

        # Act - get policies for firewall1 only
        result = repository.get_paginated(db_firewall1.id, pagination)

        # Assert
        assert len(result.items) == 3
        assert result.total == 3
        for item in result.items:
            assert item.firewall_id == db_firewall1.id

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
        repository = SQLAlchemyFilteringPolicyRepository(db_session)
        
        # Create policy to get database model
        created_policy = repository.create(policy)
        db_session.commit()
        
        db_policy = db_session.query(SQLFilteringPolicy).filter_by(id=created_policy.id).first()

        # Act
        entity = repository._to_entity(db_policy)

        # Assert
        assert isinstance(entity, FilteringPolicy)
        assert entity.id == db_policy.id
        assert entity.firewall_id == db_policy.firewall_id
        assert entity.name == db_policy.name
        assert entity.description == db_policy.description
        assert entity.priority == db_policy.priority
        assert entity.action == PolicyActionEnum(db_policy.action)
        assert entity.status == PolicyStatusEnum(db_policy.status)

    @pytest.mark.parametrize("action", [PolicyActionEnum.ALLOW, PolicyActionEnum.DENY])
    def test_create_policy_with_different_actions(self, db_session, action):
        """Test creating policies with different actions."""
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

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id, action=action)
        repository = SQLAlchemyFilteringPolicyRepository(db_session)

        # Act
        created_policy = repository.create(policy)

        # Assert
        assert created_policy.action == action
        
        # Verify in database
        db_policy = db_session.query(SQLFilteringPolicy).filter_by(id=created_policy.id).first()
        assert db_policy.action == action.value

    @pytest.mark.parametrize("status", [PolicyStatusEnum.ACTIVE, PolicyStatusEnum.INACTIVE])
    def test_create_policy_with_different_statuses(self, db_session, status):
        """Test creating policies with different statuses."""
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

        policy = FilteringPolicyFactory.build(firewall_id=db_firewall.id, status=status)
        repository = SQLAlchemyFilteringPolicyRepository(db_session)

        # Act
        created_policy = repository.create(policy)

        # Assert
        assert created_policy.status == status
        
        # Verify in database
        db_policy = db_session.query(SQLFilteringPolicy).filter_by(id=created_policy.id).first()
        assert db_policy.status == status.value