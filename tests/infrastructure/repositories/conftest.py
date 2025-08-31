"""Repository test fixtures and configuration."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.models import Base


@pytest.fixture(scope="session")
def repository_test_db_engine():
    """Create a test database engine specifically for repository tests."""
    # Use in-memory SQLite for repository tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def repository_db_session(repository_test_db_engine):
    """Create a test database session for repository tests."""
    Session = sessionmaker(bind=repository_test_db_engine)
    session = Session()

    # Start a transaction
    transaction = session.begin()

    yield session

    # Rollback transaction and close session
    transaction.rollback()
    session.close()


@pytest.fixture
def user_repository_with_session(repository_db_session):
    """Create a User repository with test database session."""
    from src.infrastructure.repositories.auth.sqlalchemy_user_repository import (
        SQLAlchemyUserRepository,
    )
    return SQLAlchemyUserRepository(repository_db_session)


@pytest.fixture
def firewall_repository_with_session(repository_db_session):
    """Create a Firewall repository with test database session."""
    from src.infrastructure.repositories.firewall.sqlalchemy_firewall_repository import (
        SQLAlchemyFirewallRepository,
    )
    return SQLAlchemyFirewallRepository(repository_db_session)


@pytest.fixture
def filtering_policy_repository_with_session(repository_db_session):
    """Create a FilteringPolicy repository with test database session."""
    from src.infrastructure.repositories.filtering_policy.sqlalchemy_filtering_policy_repository import (
        SQLAlchemyFilteringPolicyRepository,
    )
    return SQLAlchemyFilteringPolicyRepository(repository_db_session)


@pytest.fixture
def firewall_rule_repository_with_session(repository_db_session):
    """Create a FirewallRule repository with test database session."""
    from src.infrastructure.repositories.firewall_rule.sqlalchemy_firewall_rule_repository import (
        SQLAlchemyFirewallRuleRepository,
    )
    return SQLAlchemyFirewallRuleRepository(repository_db_session)


@pytest.fixture
def sample_entities_in_db(repository_db_session):
    """Create sample entities in the database for integration tests."""
    from src.infrastructure.database.models import (
        SQLFilteringPolicy,
        SQLFirewall,
        SQLFirewallRule,
        SQLUser,
    )
    from tests.factories.filtering_policy_factories import FilteringPolicyFactory
    from tests.factories.firewall_factories import FirewallFactory
    from tests.factories.firewall_rule_factories import FirewallRuleFactory
    from tests.factories.user_factories import UserFactory

    # Create users
    users = UserFactory.batch(3)
    db_users = []
    for user in users:
        db_user = SQLUser(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            status=user.status.value,
            role=user.role.value,
        )
        repository_db_session.add(db_user)
        db_users.append(db_user)

    # Create firewalls
    firewalls = FirewallFactory.batch(2)
    db_firewalls = []
    for firewall in firewalls:
        db_firewall = SQLFirewall(
            name=firewall.name,
            description=firewall.description,
            environment=firewall.environment,
            scope=firewall.scope,
        )
        repository_db_session.add(db_firewall)
        db_firewalls.append(db_firewall)

    repository_db_session.flush()

    # Create policies for firewalls
    policies = []
    db_policies = []
    for db_firewall in db_firewalls:
        firewall_policies = FilteringPolicyFactory.batch(2, firewall_id=db_firewall.id)
        policies.extend(firewall_policies)
        for policy in firewall_policies:
            db_policy = SQLFilteringPolicy(
                firewall_id=policy.firewall_id,
                name=policy.name,
                description=policy.description,
                priority=policy.priority,
                action=policy.action.value,
                status=policy.status.value,
            )
            repository_db_session.add(db_policy)
            db_policies.append(db_policy)

    repository_db_session.flush()

    # Create rules for policies
    rules = []
    db_rules = []
    for db_policy in db_policies:
        policy_rules = FirewallRuleFactory.batch(2, policy_id=db_policy.id)
        rules.extend(policy_rules)
        for rule in policy_rules:
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
            repository_db_session.add(db_rule)
            db_rules.append(db_rule)

    repository_db_session.commit()

    return {
        "users": users,
        "db_users": db_users,
        "firewalls": firewalls,
        "db_firewalls": db_firewalls,
        "policies": policies,
        "db_policies": db_policies,
        "rules": rules,
        "db_rules": db_rules,
    }