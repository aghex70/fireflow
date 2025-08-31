from datetime import datetime, timezone
from ipaddress import ip_network

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, validates


Base = declarative_base()

# SQLAlchemy Enums
IpProtocol = Enum("tcp", "udp", name="ip_protocol", native_enum=False)
RuleAction = Enum("allow", "deny", "reject", name="rule_action", native_enum=False)
PolicyAction = Enum("allow", "deny", "log", name="policy_action", native_enum=False)
PolicyStatus = Enum("active", "inactive", name="policy_status", native_enum=False)
UserStatus = Enum("active", "inactive", name="user_status", native_enum=False)
FirewallEnvironment = Enum(
    "production",
    "staging",
    "development",
    name="firewall_environment",
    native_enum=False,
)
UserRole = Enum("admin", "operator", "viewer", name="user_role", native_enum=False)


class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SQLFirewall(Base, TimestampMixin):
    """SQLAlchemy model for Firewall entity."""

    __tablename__ = "firewalls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    environment = Column(FirewallEnvironment, nullable=False, index=True)
    scope = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    policies = relationship(
        "SQLFilteringPolicy", back_populates="firewall", cascade="all, delete-orphan"
    )


class SQLFilteringPolicy(Base, TimestampMixin):
    """SQLAlchemy model for FilteringPolicy entity."""

    __tablename__ = "filtering_policies"

    id = Column(Integer, primary_key=True, index=True)
    firewall_id = Column(
        Integer, ForeignKey("firewalls.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=100)
    action = Column(PolicyAction, nullable=False, default="allow")
    status = Column(PolicyStatus, nullable=False, default="active")

    # Relationships
    firewall = relationship("SQLFirewall", back_populates="policies")
    rules = relationship(
        "SQLFirewallRule", back_populates="policy", cascade="all, delete-orphan"
    )


class SQLFirewallRule(Base, TimestampMixin):
    """SQLAlchemy model for FirewallRule entity."""

    __tablename__ = "firewall_rules"

    id = Column(Integer, primary_key=True)
    policy_id = Column(
        Integer, ForeignKey("filtering_policies.id", ondelete="CASCADE"), nullable=False
    )

    order_index = Column(
        Integer, nullable=False
    )  # first-match-wins (higher index = higher priority)

    # IPv4 CIDR max length = 18 (255.255.255.255/32)
    # IPv6 CIDR max length = 43 (ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128)
    source_cidr = Column(String(43), nullable=True)
    destination_cidr = Column(String(43), nullable=True)
    protocol = Column(IpProtocol, nullable=False, default="tcp")

    source_port_minimum = Column(Integer, nullable=True)
    source_port_maximum = Column(Integer, nullable=True)
    destination_port_minimum = Column(Integer, nullable=True)
    destination_port_maximum = Column(Integer, nullable=True)

    action = Column(RuleAction, nullable=False)

    # Relationships
    policy = relationship("SQLFilteringPolicy", back_populates="rules")

    __table_args__ = (
        UniqueConstraint(
            "policy_id",
            "order_index",
            name="uq_policy_id_order_index",
        ),
        CheckConstraint(
            "(source_port_minimum IS NULL AND source_port_maximum IS NULL) OR "
            "(source_port_minimum BETWEEN 1 AND 65535 AND "
            " source_port_maximum BETWEEN 1 AND 65535 AND "
            " source_port_minimum <= source_port_maximum)",
            name="ck_src_ports_pair_and_range",
        ),
        CheckConstraint(
            "(destination_port_minimum IS NULL AND destination_port_maximum IS NULL) OR "
            "(destination_port_minimum BETWEEN 1 AND 65535 AND "
            " destination_port_maximum BETWEEN 1 AND 65535 AND "
            " destination_port_minimum <= destination_port_maximum)",
            name="ck_dst_ports_pair_and_range",
        ),
        CheckConstraint(
            "(source_cidr IS NULL OR destination_cidr IS NULL) OR "
            "((instr(source_cidr, ':') > 0) = (instr(destination_cidr, ':') > 0))",
            name="ck_same_ip_family_if_both_set",
        ),
        Index("ix_rules_policy_order", "policy_id", "order_index"),
    )

    @validates("source_cidr", "destination_cidr")
    def _normalize_cidr(self, key, value):
        if value is None or str(value).strip() == "":
            return None
        try:
            return str(ip_network(value, strict=False))
        except Exception as e:
            raise ValueError(
                f"{key} must be a valid IPv4/IPv6 CIDR (e.g. 10.0.0.0/24 or ::/0). Received: {value}"
            ) from e


class SQLUser(Base, TimestampMixin):
    """SQLAlchemy model for User entity."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    status = Column(UserStatus, nullable=False, default="active")
    last_login = Column(DateTime, nullable=True)
    role = Column(UserRole, nullable=False, default="viewer")
