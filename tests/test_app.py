import os
import tempfile
import pytest

from src.app import create_app
from src.infrastructure.config.settings import reload_settings


@pytest.fixture
def app():
    """Create and configure a test app."""
    # Create temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set environment variable for test database
    os.environ["DB_URL"] = f"sqlite:///{db_path}"
    
    try:
        # Reload settings to pick up the new database URL
        reload_settings()
        app = create_app()
        app.config["TESTING"] = True
        yield app
    finally:
        # Clean up
        os.unlink(db_path)
        if "DB_URL" in os.environ:
            del os.environ["DB_URL"]


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "FireFlow"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "Welcome to FireFlow API" in data["message"]
    assert "endpoints" in data


def test_create_firewall(client):
    """Test creating a firewall (expects authentication error)."""
    firewall_data = {
        "name": "Test Firewall",
        "environment": "development",
        "scope": "internal",
        "description": "A test firewall"
    }

    response = client.post("/api/v1/firewalls", json=firewall_data)
    # Expects 401 because authentication is required
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_get_all_firewalls(client):
    """Test getting all firewalls (expects authentication error)."""
    response = client.get("/api/v1/firewalls")
    # Expects 401 because authentication is required  
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_create_firewall_validation_error(client):
    """Test creating firewall with validation error."""
    firewall_data = {
        "name": "",  # Empty name should cause validation error
        "environment": "development",
        "scope": "internal"
    }

    response = client.post("/api/v1/firewalls", json=firewall_data)
    # Expects 422 because schema validation happens before auth check
    assert response.status_code == 422
    data = response.get_json()
    # Validation errors are returned as a list
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in str(data[0])  # Should contain validation error for name field


def test_task_endpoints(client):
    """Test task monitoring endpoints."""
    # Test task stats endpoint
    response = client.get("/api/v1/tasks/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "active_tasks" in data
    assert "worker_count" in data
