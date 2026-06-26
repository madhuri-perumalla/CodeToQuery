"""API tests."""
from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_project(client: TestClient) -> None:
    """Test project creation."""
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "A test project",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert "id" in data


def test_list_projects(client: TestClient) -> None:
    """Test listing projects."""
    # Create a project first
    client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "A test project",
        },
    )
    
    # List projects
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1
