"""Tests for FirewallRule domain entity."""

import pytest

from src.domain.entities.firewall_rule.firewall_rule import (
    FirewallRule,
    RuleActionEnum,
    RuleProtocolEnum,
)


class TestFirewallRule:
    """Test cases for FirewallRule entity."""

    def test_rule_creation_with_required_fields(self):
        """Test rule creation with required fields."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1
        )

        assert rule.policy_id == 1
        assert rule.order_index == 1
        assert rule.id is None
        assert rule.source_cidr is None
        assert rule.destination_cidr is None
        assert rule.protocol == RuleProtocolEnum.TCP  # Default value
        assert rule.source_port_minimum is None
        assert rule.source_port_maximum is None
        assert rule.destination_port_minimum is None
        assert rule.destination_port_maximum is None
        assert rule.action == RuleActionEnum.ALLOW  # Default value

    def test_rule_creation_with_all_fields(self):
        """Test rule creation with all fields specified."""
        rule = FirewallRule(
            id=1,
            policy_id=2,
            order_index=5,
            source_cidr="192.168.1.0/24",
            destination_cidr="10.0.0.0/8",
            protocol=RuleProtocolEnum.UDP,
            source_port_minimum=8000,
            source_port_maximum=8999,
            destination_port_minimum=80,
            destination_port_maximum=80,
            action=RuleActionEnum.DENY
        )

        assert rule.id == 1
        assert rule.policy_id == 2
        assert rule.order_index == 5
        assert rule.source_cidr == "192.168.1.0/24"
        assert rule.destination_cidr == "10.0.0.0/8"
        assert rule.protocol == RuleProtocolEnum.UDP
        assert rule.source_port_minimum == 8000
        assert rule.source_port_maximum == 8999
        assert rule.destination_port_minimum == 80
        assert rule.destination_port_maximum == 80
        assert rule.action == RuleActionEnum.DENY

    @pytest.mark.parametrize("protocol", [
        RuleProtocolEnum.TCP,
        RuleProtocolEnum.UDP
    ])
    def test_rule_with_different_protocols(self, protocol):
        """Test rule creation with different protocols."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1,
            protocol=protocol
        )

        assert rule.protocol == protocol

    @pytest.mark.parametrize("action", [
        RuleActionEnum.ALLOW,
        RuleActionEnum.DENY,
        RuleActionEnum.REJECT
    ])
    def test_rule_with_different_actions(self, action):
        """Test rule creation with different actions."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1,
            action=action
        )

        assert rule.action == action

    def test_rule_with_port_ranges(self):
        """Test rule creation with port ranges."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1,
            source_port_minimum=1000,
            source_port_maximum=2000,
            destination_port_minimum=80,
            destination_port_maximum=443
        )

        assert rule.source_port_minimum == 1000
        assert rule.source_port_maximum == 2000
        assert rule.destination_port_minimum == 80
        assert rule.destination_port_maximum == 443

    def test_rule_with_single_ports(self):
        """Test rule creation with single ports."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1,
            destination_port_minimum=80,
            destination_port_maximum=80
        )

        assert rule.destination_port_minimum == 80
        assert rule.destination_port_maximum == 80

    def test_rule_with_cidr_blocks(self):
        """Test rule creation with CIDR blocks."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1,
            source_cidr="192.168.1.0/24",
            destination_cidr="10.0.0.0/8"
        )

        assert rule.source_cidr == "192.168.1.0/24"
        assert rule.destination_cidr == "10.0.0.0/8"

    def test_rule_equality(self):
        """Test rule equality comparison."""
        rule1 = FirewallRule(
            id=1,
            policy_id=1,
            order_index=1,
            protocol=RuleProtocolEnum.TCP
        )

        rule2 = FirewallRule(
            id=1,
            policy_id=1,
            order_index=1,
            protocol=RuleProtocolEnum.TCP
        )

        rule3 = FirewallRule(
            id=2,
            policy_id=1,
            order_index=1,
            protocol=RuleProtocolEnum.TCP
        )

        assert rule1 == rule2
        assert rule1 != rule3

    def test_rule_string_representation(self):
        """Test rule string representation."""
        rule = FirewallRule(
            id=1,
            policy_id=1,
            order_index=1,
            protocol=RuleProtocolEnum.TCP,
            action=RuleActionEnum.ALLOW
        )

        str_repr = str(rule)
        assert "FirewallRule" in str_repr or str(rule.id) in str_repr

    def test_rule_protocol_enum_values(self):
        """Test that protocol enum has correct values."""
        assert RuleProtocolEnum.TCP.value == "tcp"
        assert RuleProtocolEnum.UDP.value == "udp"

    def test_rule_action_enum_values(self):
        """Test that action enum has correct values."""
        assert RuleActionEnum.ALLOW.value == "allow"
        assert RuleActionEnum.DENY.value == "deny"
        assert RuleActionEnum.REJECT.value == "reject"

    def test_rule_default_values(self):
        """Test that rule uses correct default values."""
        rule = FirewallRule(
            policy_id=1,
            order_index=1
        )

        assert rule.protocol == RuleProtocolEnum.TCP
        assert rule.action == RuleActionEnum.ALLOW

    @pytest.mark.parametrize("order_index", [1, 5, 10, 100])
    def test_rule_with_different_order_indices(self, order_index):
        """Test rule creation with different order indices."""
        rule = FirewallRule(
            policy_id=1,
            order_index=order_index
        )

        assert rule.order_index == order_index