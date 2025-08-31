"""Tests for Firewall domain entity."""

import pytest

from src.domain.entities.firewall.firewall import Firewall, FirewallEnvironmentEnum


class TestFirewall:
    """Test cases for Firewall entity."""

    def test_firewall_creation_with_required_fields(self):
        """Test firewall creation with required fields."""
        firewall = Firewall(
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test"
        )

        assert firewall.name == "Test Firewall"
        assert firewall.environment == FirewallEnvironmentEnum.PRODUCTION
        assert firewall.scope == "test"
        assert firewall.id is None
        assert firewall.description is None

    def test_firewall_creation_with_all_fields(self):
        """Test firewall creation with all fields specified."""
        firewall = Firewall(
            id=1,
            name="Production Firewall",
            description="Main production firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="production"
        )

        assert firewall.id == 1
        assert firewall.name == "Production Firewall"
        assert firewall.description == "Main production firewall"
        assert firewall.environment == FirewallEnvironmentEnum.PRODUCTION
        assert firewall.scope == "production"

    @pytest.mark.parametrize("environment", [
        FirewallEnvironmentEnum.PRODUCTION,
        FirewallEnvironmentEnum.STAGING,
        FirewallEnvironmentEnum.DEVELOPMENT
    ])
    def test_firewall_with_different_environments(self, environment):
        """Test firewall creation with different environments."""
        firewall = Firewall(
            name="Test Firewall",
            environment=environment,
            scope="test"
        )

        assert firewall.environment == environment

    def test_firewall_equality(self):
        """Test firewall equality comparison."""
        firewall1 = Firewall(
            id=1,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test"
        )

        firewall2 = Firewall(
            id=1,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test"
        )

        firewall3 = Firewall(
            id=2,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test"
        )

        assert firewall1 == firewall2
        assert firewall1 != firewall3

    def test_firewall_string_representation(self):
        """Test firewall string representation."""
        firewall = Firewall(
            id=1,
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.PRODUCTION,
            scope="test"
        )

        str_repr = str(firewall)
        assert "Test Firewall" in str_repr

    def test_firewall_environment_enum_values(self):
        """Test that environment enum has correct values."""
        assert FirewallEnvironmentEnum.PRODUCTION.value == "production"
        assert FirewallEnvironmentEnum.STAGING.value == "staging"
        assert FirewallEnvironmentEnum.DEVELOPMENT.value == "development"

    def test_firewall_with_optional_description(self):
        """Test firewall with optional description field."""
        firewall_with_desc = Firewall(
            name="Test Firewall",
            description="A test firewall",
            environment=FirewallEnvironmentEnum.DEVELOPMENT,
            scope="test"
        )

        firewall_without_desc = Firewall(
            name="Test Firewall",
            environment=FirewallEnvironmentEnum.DEVELOPMENT,
            scope="test"
        )

        assert firewall_with_desc.description == "A test firewall"
        assert firewall_without_desc.description is None