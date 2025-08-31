"""Tests for Firewall use cases."""

from unittest.mock import Mock

import pytest

from src.domain.entities.firewall.firewall import Firewall, FirewallEnvironmentEnum
from src.domain.use_cases.firewall.create_firewall_use_case import (
    CreateFirewallUseCase,
)
from src.domain.use_cases.firewall.delete_firewall_use_case import (
    DeleteFirewallUseCase,
)
from src.domain.use_cases.firewall.get_all_firewalls_use_case import (
    GetAllFirewallsUseCase,
)
from src.domain.use_cases.firewall.get_firewall_use_case import GetFirewallUseCase
from src.infrastructure.web.schemas.firewall.firewall_schemas import (
    FirewallCreateSchema,
)
from src.infrastructure.web.utils.pagination import (
    PaginationRequest,
    PaginationResponse,
)


class TestCreateFirewallUseCase:
    """Test cases for CreateFirewallUseCase."""

    def test_create_firewall_success(self):
        """Test successful firewall creation."""
        # Arrange
        mock_service = Mock()
        mock_service.get_firewall_by_name.return_value = None  # No existing firewall
        mock_service.create_firewall.return_value = Firewall(
            id=1,
            name="Test Firewall",
            description="Test Description",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )

        use_case = CreateFirewallUseCase(mock_service)
        schema = FirewallCreateSchema(
            name="Test Firewall",
            description="Test Description",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )

        # Act
        result = use_case.execute(schema)

        # Assert
        assert result.id == 1
        assert result.name == "Test Firewall"
        mock_service.get_firewall_by_name.assert_called_once_with("Test Firewall")
        mock_service.create_firewall.assert_called_once()

    def test_create_firewall_with_existing_name_raises_error(self):
        """Test that creating firewall with existing name raises error."""
        # Arrange
        mock_service = Mock()
        mock_service.get_firewall_by_name.return_value = Firewall(
            id=1,
            name="Existing Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )

        use_case = CreateFirewallUseCase(mock_service)
        schema = FirewallCreateSchema(
            name="Existing Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="Firewall with name 'Existing Firewall' already exists"
        ):
            use_case.execute(schema)


class TestGetFirewallUseCase:
    """Test cases for GetFirewallUseCase."""

    def test_get_firewall_success(self):
        """Test successful firewall retrieval."""
        # Arrange
        mock_service = Mock()
        expected_firewall = Firewall(
            id=1,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )
        mock_service.get_firewall_by_id.return_value = expected_firewall

        use_case = GetFirewallUseCase(mock_service)

        # Act
        result = use_case.execute(1)

        # Assert
        assert result == expected_firewall
        mock_service.get_firewall_by_id.assert_called_once_with(1)

    def test_get_firewall_not_found_raises_error(self):
        """Test that getting non-existent firewall raises error."""
        # Arrange
        mock_service = Mock()
        mock_service.get_firewall_by_id.return_value = None

        use_case = GetFirewallUseCase(mock_service)

        # Act & Assert
        with pytest.raises(ValueError, match="Firewall with id 999 not found"):
            use_case.execute(999)


class TestGetAllFirewallsUseCase:
    """Test cases for GetAllFirewallsUseCase."""

    def test_get_all_firewalls_success(self):
        """Test successful retrieval of all firewalls."""
        # Arrange
        mock_service = Mock()
        expected_firewalls = [
            Firewall(
                id=1,
                name="Firewall 1",
                environment=FirewallEnvironmentEnum.PRODUCTION,
                scope="test",
            ),
            Firewall(
                id=2,
                name="Firewall 2",
                environment=FirewallEnvironmentEnum.STAGING,
                scope="test",
            ),
        ]
        expected_response = PaginationResponse(
            page=1,
            size=10,
            total=2,
            total_pages=1,
            has_next=False,
            has_previous=False,
            items=expected_firewalls,
        )
        mock_service.get_all_firewalls.return_value = expected_response

        use_case = GetAllFirewallsUseCase(mock_service)
        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = use_case.execute(pagination)

        # Assert
        assert result == expected_response
        mock_service.get_all_firewalls.assert_called_once_with(pagination)

    def test_get_all_firewalls_empty_list(self):
        """Test retrieval when no firewalls exist."""
        # Arrange
        mock_service = Mock()
        empty_response = PaginationResponse(
            page=1,
            size=10,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
            items=[],
        )
        mock_service.get_all_firewalls.return_value = empty_response

        use_case = GetAllFirewallsUseCase(mock_service)
        pagination = PaginationRequest(page=1, size=10)

        # Act
        result = use_case.execute(pagination)

        # Assert
        assert result == empty_response


class TestDeleteFirewallUseCase:
    """Test cases for DeleteFirewallUseCase."""

    def test_delete_firewall_success(self):
        """Test successful firewall deletion."""
        # Arrange
        mock_service = Mock()
        existing_firewall = Firewall(
            id=1,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test",
        )
        mock_service.get_firewall_by_id.return_value = existing_firewall
        mock_service.delete_firewall.return_value = True

        use_case = DeleteFirewallUseCase(mock_service)

        # Act
        result = use_case.execute(1)

        # Assert
        assert result is True
        mock_service.get_firewall_by_id.assert_called_once_with(1)
        mock_service.delete_firewall.assert_called_once_with(1)

    def test_delete_firewall_not_found_raises_error(self):
        """Test that deleting non-existent firewall raises error."""
        # Arrange
        mock_service = Mock()
        mock_service.get_firewall_by_id.return_value = None

        use_case = DeleteFirewallUseCase(mock_service)

        # Act & Assert
        with pytest.raises(ValueError, match="Firewall with id 999 not found"):
            use_case.execute(999)