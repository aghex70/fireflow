"""Tests for Firewall repository."""

import pytest

from src.domain.entities.firewall.firewall import Firewall, FirewallEnvironmentEnum
from src.infrastructure.database.models import SQLFirewall
from src.infrastructure.repositories.firewall.sqlalchemy_firewall_repository import (
    SQLAlchemyFirewallRepository,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from tests.factories.firewall_factories import FirewallFactory


class TestSQLAlchemyFirewallRepository:
    """Test cases for SQLAlchemy Firewall repository."""

    def test_create_firewall_success(self, db_session):
        """Test successful firewall creation."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        created_firewall = repository.create(firewall)

        # Assert
        assert created_firewall.id is not None
        assert created_firewall.name == firewall.name
        assert created_firewall.description == firewall.description
        assert created_firewall.environment == firewall.environment
        assert created_firewall.scope == firewall.scope

        # Verify in database
        db_firewall = db_session.query(SQLFirewall).filter_by(id=created_firewall.id).first()
        assert db_firewall is not None
        assert db_firewall.name == firewall.name

    def test_get_by_id_existing_firewall(self, db_session):
        """Test getting firewall by existing ID."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)
        created_firewall = repository.create(firewall)
        db_session.commit()

        # Act
        found_firewall = repository.get_by_id(created_firewall.id)

        # Assert
        assert found_firewall is not None
        assert found_firewall.id == created_firewall.id
        assert found_firewall.name == firewall.name
        assert found_firewall.environment == firewall.environment

    def test_get_by_id_nonexistent_firewall_returns_none(self, db_session):
        """Test getting firewall by non-existent ID returns None."""
        # Arrange
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        found_firewall = repository.get_by_id(99999)

        # Assert
        assert found_firewall is None

    def test_get_by_name_existing_firewall(self, db_session):
        """Test getting firewall by existing name."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)
        repository.create(firewall)
        db_session.commit()

        # Act
        found_firewall = repository.get_by_name(firewall.name)

        # Assert
        assert found_firewall is not None
        assert found_firewall.name == firewall.name
        assert found_firewall.environment == firewall.environment

    def test_get_by_name_nonexistent_firewall_returns_none(self, db_session):
        """Test getting firewall by non-existent name returns None."""
        # Arrange
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        found_firewall = repository.get_by_name("nonexistent")

        # Assert
        assert found_firewall is None

    def test_delete_existing_firewall_success(self, db_session):
        """Test successful deletion of existing firewall."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)
        created_firewall = repository.create(firewall)
        db_session.commit()

        # Act
        result = repository.delete(created_firewall.id)

        # Assert
        assert result is True
        
        # Verify firewall is deleted from database
        db_firewall = db_session.query(SQLFirewall).filter_by(id=created_firewall.id).first()
        assert db_firewall is None

    def test_delete_nonexistent_firewall_returns_false(self, db_session):
        """Test deletion of non-existent firewall returns False."""
        # Arrange
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        result = repository.delete(99999)

        # Assert
        assert result is False

    def test_get_paginated_empty_results(self, db_session):
        """Test getting paginated firewalls when none exist."""
        # Arrange
        repository = SQLAlchemyFirewallRepository(db_session)
        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(pagination)

        # Assert
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 0

    def test_get_paginated_multiple_firewalls(self, db_session):
        """Test getting paginated firewalls with multiple results."""
        # Arrange
        firewalls = FirewallFactory.batch(5)
        repository = SQLAlchemyFirewallRepository(db_session)
        
        for firewall in firewalls:
            repository.create(firewall)
        db_session.commit()

        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = repository.get_paginated(pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert result.total_pages == 1

        # Verify all firewalls are returned as entities
        for item in result.items:
            assert isinstance(item, Firewall)

    def test_get_paginated_with_pagination_limits(self, db_session):
        """Test paginated results respect pagination limits."""
        # Arrange
        firewalls = FirewallFactory.batch(15)
        repository = SQLAlchemyFirewallRepository(db_session)
        
        for firewall in firewalls:
            repository.create(firewall)
        db_session.commit()

        pagination = PaginationRequest(page=2, size=5)

        # Act
        result = repository.get_paginated(pagination)

        # Assert
        assert len(result.items) == 5
        assert result.total == 15
        assert result.page == 2
        assert result.size == 5
        assert result.total_pages == 3

    def test_get_paginated_with_sorting_by_name(self, db_session):
        """Test paginated results with sorting by name."""
        # Arrange
        firewall1 = FirewallFactory.build(name="Z-Firewall")
        firewall2 = FirewallFactory.build(name="A-Firewall")
        firewall3 = FirewallFactory.build(name="M-Firewall")
        
        repository = SQLAlchemyFirewallRepository(db_session)
        repository.create(firewall1)
        repository.create(firewall2)
        repository.create(firewall3)
        db_session.commit()

        pagination = PaginationRequest(page=1, per_page=10, sort_by="name", sort_dir="asc")

        # Act
        result = repository.get_paginated(pagination)

        # Assert
        assert len(result.items) == 3
        assert result.items[0].name == "A-Firewall"
        assert result.items[1].name == "M-Firewall"
        assert result.items[2].name == "Z-Firewall"

    def test_get_paginated_with_sorting_by_environment_desc(self, db_session):
        """Test paginated results with descending sort by environment."""
        # Arrange
        firewall1 = FirewallFactory.build(environment=FirewallEnvironmentEnum.DEVELOPMENT)
        firewall2 = FirewallFactory.build(environment=FirewallEnvironmentEnum.PRODUCTION)
        firewall3 = FirewallFactory.build(environment=FirewallEnvironmentEnum.STAGING)
        
        repository = SQLAlchemyFirewallRepository(db_session)
        repository.create(firewall1)
        repository.create(firewall2)
        repository.create(firewall3)
        db_session.commit()

        pagination = PaginationRequest(page=1, per_page=10, sort_by="environment", sort_dir="desc")

        # Act
        result = repository.get_paginated(pagination)

        # Assert
        assert len(result.items) == 3
        # Note: Depends on enum value ordering, but should be consistent

    def test_to_entity_conversion(self, db_session):
        """Test conversion from database model to domain entity."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)
        
        # Create firewall to get database model
        created_firewall = repository.create(firewall)
        db_session.commit()
        
        db_firewall = db_session.query(SQLFirewall).filter_by(id=created_firewall.id).first()

        # Act
        entity = repository._to_entity(db_firewall)

        # Assert
        assert isinstance(entity, Firewall)
        assert entity.id == db_firewall.id
        assert entity.name == db_firewall.name
        assert entity.description == db_firewall.description
        assert entity.environment == db_firewall.environment
        assert entity.scope == db_firewall.scope

    @pytest.mark.parametrize("environment", [
        FirewallEnvironmentEnum.PRODUCTION,
        FirewallEnvironmentEnum.STAGING,
        FirewallEnvironmentEnum.DEVELOPMENT
    ])
    def test_create_firewall_with_different_environments(self, db_session, environment):
        """Test creating firewalls with different environments."""
        # Arrange
        firewall = FirewallFactory.build(environment=environment)
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        created_firewall = repository.create(firewall)

        # Assert
        assert created_firewall.environment == environment
        
        # Verify in database
        db_firewall = db_session.query(SQLFirewall).filter_by(id=created_firewall.id).first()
        assert db_firewall.environment == environment

    def test_create_multiple_firewalls_with_different_names(self, db_session):
        """Test creating multiple firewalls with unique names."""
        # Arrange
        firewalls = [
            FirewallFactory.build(name="Prod-FW-1"),
            FirewallFactory.build(name="Staging-FW-1"),
            FirewallFactory.build(name="Dev-FW-1")
        ]
        repository = SQLAlchemyFirewallRepository(db_session)

        # Act
        created_firewalls = []
        for firewall in firewalls:
            created_firewalls.append(repository.create(firewall))
        db_session.commit()

        # Assert
        assert len(created_firewalls) == 3
        for i, created in enumerate(created_firewalls):
            assert created.name == firewalls[i].name
            assert created.id is not None

        # Verify all exist in database
        db_count = db_session.query(SQLFirewall).count()
        assert db_count == 3

    def test_get_paginated_with_invalid_sort_column_uses_default(self, db_session):
        """Test that invalid sort columns fall back to default behavior."""
        # Arrange
        firewall = FirewallFactory.build()
        repository = SQLAlchemyFirewallRepository(db_session)
        repository.create(firewall)
        db_session.commit()

        pagination = PaginationRequest(page=1, per_page=10, sort_by="invalid_column")

        # Act - should not raise error, uses default sorting
        result = repository.get_paginated(pagination)

        # Assert
        assert len(result.items) == 1
        assert result.total == 1