"""Global test configuration and fixtures."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.filtering_policy.filtering_policy import FilteringPolicy
from src.domain.entities.firewall.firewall import Firewall, FirewallEnvironmentEnum
from src.domain.entities.firewall_rule.firewall_rule import FirewallRule
from src.infrastructure.database.models import Base
from tests.factories.filtering_policy_factories import FilteringPolicyFactory
from tests.factories.firewall_factories import FirewallFactory
from tests.factories.firewall_rule_factories import FirewallRuleFactory
from tests.factories.user_factories import UserFactory


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a test database session with transaction isolation."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    # Always rollback the transaction to ensure test isolation
    session.close()
    try:
        transaction.rollback()
    except Exception:
        # Transaction may already be rolled back
        pass
    connection.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("redis.from_url") as mock_redis_client:
        mock_client = MagicMock()
        mock_redis_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_celery():
    """Mock Celery app for testing."""
    with patch("infrastructure.celery.celery_app.celery_app") as mock_celery_app:
        mock_task = MagicMock()
        mock_task.delay.return_value.id = "test-task-id"
        mock_celery_app.task.return_value = mock_task
        yield mock_celery_app


@pytest.fixture
def sample_firewall():
    """Create a sample firewall entity."""
    return Firewall(
        id=1,
        name="Test Firewall",
        description="A test firewall",
        environment=FirewallEnvironmentEnum.PRODUCTION,
        scope="test",
    )


@pytest.fixture
def sample_policy():
    """Create a sample filtering policy entity."""
    from src.domain.entities.filtering_policy.filtering_policy import PolicyActionEnum, PolicyStatusEnum
    return FilteringPolicy(
        id=1,
        firewall_id=1,
        name="Test Policy",
        description="A test policy",
        priority=100,
        action=PolicyActionEnum.ALLOW,
        status=PolicyStatusEnum.ACTIVE,
    )


@pytest.fixture
def sample_rule():
    """Create a sample firewall rule entity."""
    from src.domain.entities.firewall_rule.firewall_rule import RuleActionEnum, RuleProtocolEnum
    return FirewallRule(
        id=1,
        policy_id=1,
        order_index=1,
        source_cidr="192.168.1.0/24",
        destination_cidr="10.0.0.0/8",
        protocol=RuleProtocolEnum.TCP,
        destination_port_minimum=80,
        destination_port_maximum=80,
        action=RuleActionEnum.ALLOW,
    )


@pytest.fixture
def sample_firewall_data():
    """Sample firewall data for API tests."""
    return {
        "name": "API Test Firewall",
        "description": "Firewall created via API test",
        "ip_address": "10.0.0.1",
        "port": 443,
        "status": "active",
    }


@pytest.fixture
def sample_policy_data():
    """Sample policy data for API tests."""
    return {
        "firewall_id": 1,
        "name": "API Test Policy",
        "description": "Policy created via API test",
        "priority": 50,
        "action": "deny",
        "is_enabled": True,
    }


@pytest.fixture
def sample_rule_data():
    """Sample rule data for API tests."""
    return {
        "policy_id": 1,
        "name": "API Test Rule",
        "description": "Rule created via API test",
        "source_ip": "0.0.0.0/0",
        "destination_ip": "192.168.1.100",
        "destination_port": "443",
        "protocol": "tcp",
        "action": "allow",
        "direction": "inbound",
        "is_enabled": True,
    }


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        log_dir.mkdir()
        yield log_dir


@pytest.fixture
def mock_logger():
    """Mock structlog logger."""
    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance


@pytest.fixture
def app_config():
    """Test application configuration."""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "CELERY_BROKER_URL": "memory://",
        "CELERY_RESULT_BACKEND": "cache+memory://",
        "CACHE_TYPE": "simple",
        "SECRET_KEY": "test-secret-key",
    }


@pytest.fixture
def flask_app(app_config):
    """Create Flask application for testing."""
    from app import create_app

    # Mock Celery to avoid Redis dependency in tests
    with patch("infrastructure.celery.celery_app.make_celery"):
        app = create_app()
        app.config.update(app_config)

        with app.app_context():
            yield app


@pytest.fixture
def client(flask_app):
    """Create test client."""
    return flask_app.test_client()


@pytest.fixture
def runner(flask_app):
    """Create test runner."""
    return flask_app.test_cli_runner()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["CELERY_BROKER_URL"] = "memory://"
    os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"


# Polyfactory-based fixtures
@pytest.fixture
def firewall_factory():
    """Provide FirewallFactory for tests."""
    return FirewallFactory


@pytest.fixture
def filtering_policy_factory():
    """Provide FilteringPolicyFactory for tests."""
    return FilteringPolicyFactory


@pytest.fixture
def firewall_rule_factory():
    """Provide FirewallRuleFactory for tests."""
    return FirewallRuleFactory


@pytest.fixture
def user_factory():
    """Provide UserFactory for tests."""
    return UserFactory


@pytest.fixture
def sample_firewall_from_factory():
    """Create a sample firewall using factory."""
    return FirewallFactory.build()


@pytest.fixture
def sample_policy_from_factory():
    """Create a sample filtering policy using factory."""
    return FilteringPolicyFactory.build()


@pytest.fixture
def sample_rule_from_factory():
    """Create a sample firewall rule using factory."""
    return FirewallRuleFactory.build()


@pytest.fixture
def production_firewall():
    """Create a production firewall using factory."""
    return FirewallFactory.production_firewall()


@pytest.fixture
def staging_firewall():
    """Create a staging firewall using factory."""
    return FirewallFactory.staging_firewall()


@pytest.fixture
def development_firewall():
    """Create a development firewall using factory."""
    return FirewallFactory.development_firewall()


@pytest.fixture
def allow_policy():
    """Create an allow filtering policy using factory."""
    return FilteringPolicyFactory.allow_policy()


@pytest.fixture
def deny_policy():
    """Create a deny filtering policy using factory."""
    return FilteringPolicyFactory.deny_policy()


@pytest.fixture
def tcp_rule():
    """Create a TCP firewall rule using factory."""
    return FirewallRuleFactory.tcp_rule()


@pytest.fixture
def udp_rule():
    """Create a UDP firewall rule using factory."""
    return FirewallRuleFactory.udp_rule()


@pytest.fixture
def http_rule():
    """Create an HTTP firewall rule using factory."""
    return FirewallRuleFactory.http_rule()


@pytest.fixture
def https_rule():
    """Create an HTTPS firewall rule using factory."""
    return FirewallRuleFactory.https_rule()


@pytest.fixture
def ssh_rule():
    """Create an SSH firewall rule using factory."""
    return FirewallRuleFactory.ssh_rule()


@pytest.fixture
def multiple_firewalls():
    """Create multiple firewalls using factory."""
    return FirewallFactory.batch(size=5)


@pytest.fixture
def multiple_policies():
    """Create multiple filtering policies using factory."""
    return FilteringPolicyFactory.batch(size=5)


@pytest.fixture
def multiple_rules():
    """Create multiple firewall rules using factory."""
    return FirewallRuleFactory.batch(size=5)


@pytest.fixture
def sample_user_from_factory():
    """Create a sample user using factory."""
    return UserFactory.build()


@pytest.fixture
def admin_user():
    """Create an admin user using factory."""
    return UserFactory.admin_user()


@pytest.fixture
def operator_user():
    """Create an operator user using factory."""
    return UserFactory.operator_user()


@pytest.fixture
def viewer_user():
    """Create a viewer user using factory."""
    return UserFactory.viewer_user()


@pytest.fixture
def active_user():
    """Create an active user using factory."""
    return UserFactory.active_user()


@pytest.fixture
def inactive_user():
    """Create an inactive user using factory."""
    return UserFactory.inactive_user()


@pytest.fixture
def suspended_user():
    """Create a suspended user using factory."""
    return UserFactory.suspended_user()


@pytest.fixture
def user_with_recent_login():
    """Create a user with recent login using factory."""
    return UserFactory.user_with_recent_login()


@pytest.fixture
def multiple_users():
    """Create multiple users using factory."""
    return UserFactory.batch(size=5)


# Markers for different test types
pytest_plugins = []


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        # Add slow marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.integration)

        # Add unit marker to unit tests
        elif any(
            folder in str(item.fspath) for folder in ["domain", "entities", "use_cases"]
        ):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to infrastructure tests
        elif "infrastructure" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
