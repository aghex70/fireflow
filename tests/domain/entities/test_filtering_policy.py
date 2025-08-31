"""Tests for FilteringPolicy domain entity."""

import pytest

from src.domain.entities.filtering_policy.filtering_policy import (
    FilteringPolicy,
    PolicyActionEnum,
    PolicyStatusEnum,
)


class TestFilteringPolicy:
    """Test cases for FilteringPolicy entity."""

    def test_policy_creation_with_required_fields(self):
        """Test policy creation with required fields."""
        policy = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        assert policy.firewall_id == 1
        assert policy.name == "Test Policy"
        assert policy.priority == 100
        assert policy.action == PolicyActionEnum.ALLOW  # Default value
        assert policy.status == PolicyStatusEnum.ACTIVE  # Default value
        assert policy.id is None
        assert policy.description is None

    def test_policy_creation_with_all_fields(self):
        """Test policy creation with all fields specified."""
        policy = FilteringPolicy(
            id=1,
            firewall_id=2,
            name="Production Policy",
            description="Main production policy",
            priority=50,
            action=PolicyActionEnum.DENY,
            status=PolicyStatusEnum.INACTIVE
        )

        assert policy.id == 1
        assert policy.firewall_id == 2
        assert policy.name == "Production Policy"
        assert policy.description == "Main production policy"
        assert policy.priority == 50
        assert policy.action == PolicyActionEnum.DENY
        assert policy.status == PolicyStatusEnum.INACTIVE

    @pytest.mark.parametrize("action", [
        PolicyActionEnum.ALLOW,
        PolicyActionEnum.DENY,
        PolicyActionEnum.LOG
    ])
    def test_policy_with_different_actions(self, action):
        """Test policy creation with different actions."""
        policy = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=100,
            action=action
        )

        assert policy.action == action

    @pytest.mark.parametrize("status", [
        PolicyStatusEnum.ACTIVE,
        PolicyStatusEnum.INACTIVE
    ])
    def test_policy_with_different_statuses(self, status):
        """Test policy creation with different statuses."""
        policy = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=100,
            status=status
        )

        assert policy.status == status

    @pytest.mark.parametrize("priority", [1, 50, 100, 999])
    def test_policy_with_different_priorities(self, priority):
        """Test policy creation with different priorities."""
        policy = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=priority
        )

        assert policy.priority == priority

    def test_policy_equality(self):
        """Test policy equality comparison."""
        policy1 = FilteringPolicy(
            id=1,
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        policy2 = FilteringPolicy(
            id=1,
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        policy3 = FilteringPolicy(
            id=2,
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        assert policy1 == policy2
        assert policy1 != policy3

    def test_policy_string_representation(self):
        """Test policy string representation."""
        policy = FilteringPolicy(
            id=1,
            firewall_id=1,
            name="Test Policy",
            priority=100,
            action=PolicyActionEnum.ALLOW
        )

        str_repr = str(policy)
        assert "Test Policy" in str_repr

    def test_policy_action_enum_values(self):
        """Test that action enum has correct values."""
        assert PolicyActionEnum.ALLOW.value == "allow"
        assert PolicyActionEnum.DENY.value == "deny"
        assert PolicyActionEnum.LOG.value == "log"

    def test_policy_status_enum_values(self):
        """Test that status enum has correct values."""
        assert PolicyStatusEnum.ACTIVE.value == "active"
        assert PolicyStatusEnum.INACTIVE.value == "inactive"

    def test_policy_with_optional_description(self):
        """Test policy with optional description field."""
        policy_with_desc = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            description="A test policy",
            priority=100
        )

        policy_without_desc = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        assert policy_with_desc.description == "A test policy"
        assert policy_without_desc.description is None

    def test_policy_default_values(self):
        """Test that policy uses correct default values."""
        policy = FilteringPolicy(
            firewall_id=1,
            name="Test Policy",
            priority=100
        )

        assert policy.action == PolicyActionEnum.ALLOW
        assert policy.status == PolicyStatusEnum.ACTIVE