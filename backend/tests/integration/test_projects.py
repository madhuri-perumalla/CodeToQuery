"""Integration tests for project management endpoints."""
import pytest

from fastapi import status


@pytest.mark.projects
class TestProjectCreation:
    """Test project creation endpoint."""

    def test_create_project_success(self, client, auth_headers, sample_project_data):
        """Test successful project creation."""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json=sample_project_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["description"] == sample_project_data["description"]
        assert "id" in data
        assert "owner_id" in data

    def test_create_project_unauthorized(self, client, sample_project_data):
        """Test project creation without authentication."""
        response = client.post(
            "/api/v1/projects",
            json=sample_project_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_project_missing_name(self, client, auth_headers):
        """Test project creation with missing name."""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"description": "Test description"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_project_empty_name(self, client, auth_headers):
        """Test project creation with empty name."""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"name": "", "description": "Test"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.projects
class TestProjectRetrieval:
    """Test project retrieval endpoints."""

    def test_get_projects_success(self, client, auth_headers, test_project):
        """Test successfully getting projects list."""
        response = client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_get_projects_unauthorized(self, client):
        """Test getting projects without authentication."""
        response = client.get("/api/v1/projects")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_project_by_id_success(self, client, auth_headers, test_project):
        """Test successfully getting a specific project."""
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name

    def test_get_project_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent project."""
        response = client.get(
            "/api/v1/projects/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_project_by_id_unauthorized(self, client, test_project):
        """Test getting project without authentication."""
        response = client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_projects_pagination(self, client, auth_headers, test_project):
        """Test projects list pagination."""
        response = client.get(
            "/api/v1/projects?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_projects_search(self, client, auth_headers, test_project):
        """Test projects list search functionality."""
        response = client.get(
            f"/api/v1/projects?search={test_project.name}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data


@pytest.mark.projects
class TestProjectUpdate:
    """Test project update endpoint."""

    def test_update_project_success(self, client, auth_headers, test_project):
        """Test successful project update."""
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description"
        }
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_project_unauthorized(self, client, test_project):
        """Test project update without authentication."""
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_project_not_found(self, client, auth_headers):
        """Test updating non-existent project."""
        response = client.put(
            "/api/v1/projects/99999",
            headers=auth_headers,
            json={"name": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_project_partial(self, client, auth_headers, test_project):
        """Test partial project update (only name)."""
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": "New Name"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.projects
class TestProjectDeletion:
    """Test project deletion endpoint."""

    def test_delete_project_success(self, client, auth_headers, test_project):
        """Test successful project deletion."""
        response = client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_project_unauthorized(self, client, test_project):
        """Test project deletion without authentication."""
        response = client.delete(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_project_not_found(self, client, auth_headers):
        """Test deleting non-existent project."""
        response = client.delete(
            "/api/v1/projects/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.projects
class TestProjectStatistics:
    """Test project statistics endpoint."""

    def test_get_project_stats_success(self, client, auth_headers, test_project):
        """Test successfully getting project statistics."""
        response = client.get(
            f"/api/v1/projects/{test_project.id}/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_codebases" in data
        assert "total_queries" in data
        assert "total_diagnostics" in data

    def test_get_project_stats_unauthorized(self, client, test_project):
        """Test getting project stats without authentication."""
        response = client.get(f"/api/v1/projects/{test_project.id}/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_project_stats_not_found(self, client, auth_headers):
        """Test getting stats for non-existent project."""
        response = client.get(
            "/api/v1/projects/99999/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.projects
class TestProjectOwnership:
    """Test project ownership and access control."""

    def test_user_cannot_access_other_users_project(self, client, test_admin_user, test_project):
        """Test that users cannot access projects owned by other users."""
        # Login as admin
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_admin_user.email,
                "password": "adminpassword123"
            }
        )
        admin_token = response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Try to access test_user's project
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=admin_headers
        )
        # Should either return 404 (not found for this user) or 403 (forbidden)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_user_can_only_see_own_projects(self, client, auth_headers, test_project, test_admin_user):
        """Test that users only see their own projects in list."""
        response = client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All projects should belong to the authenticated user
        for project in data["items"]:
            assert project["owner_id"] == test_project.owner_id


@pytest.mark.projects
class TestProjectValidation:
    """Test project data validation."""

    def test_project_name_too_long(self, client, auth_headers):
        """Test project creation with name exceeding max length."""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "name": "a" * 300,
                "description": "Test"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_project_description_too_long(self, client, auth_headers):
        """Test project creation with description exceeding max length."""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "name": "Test",
                "description": "a" * 2000
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
