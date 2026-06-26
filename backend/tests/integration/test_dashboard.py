"""Integration tests for dashboard endpoints."""
import pytest

from fastapi import status


@pytest.mark.dashboard
class TestDashboardOverview:
    """Test dashboard overview endpoint."""

    def test_get_dashboard_overview_success(self, client, auth_headers):
        """Test successfully getting dashboard overview."""
        response = client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_projects" in data
        assert "total_codebases" in data
        assert "total_queries" in data
        assert "total_diagnostics" in data

    def test_get_dashboard_overview_unauthorized(self, client):
        """Test getting dashboard overview without authentication."""
        response = client.get("/api/v1/dashboard/overview")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.dashboard
class TestDashboardStatistics:
    """Test dashboard statistics endpoints."""

    def test_get_project_statistics_success(self, client, auth_headers, test_project):
        """Test successfully getting project statistics."""
        response = client.get(
            "/api/v1/dashboard/projects/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_projects" in data
        assert "active_projects" in data

    def test_get_project_statistics_unauthorized(self, client):
        """Test getting project statistics without authentication."""
        response = client.get("/api/v1/dashboard/projects/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_query_statistics_success(self, client, auth_headers):
        """Test successfully getting query statistics."""
        response = client.get(
            "/api/v1/dashboard/queries/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_queries" in data
        assert "queries_with_diagnostics" in data

    def test_get_query_statistics_unauthorized(self, client):
        """Test getting query statistics without authentication."""
        response = client.get("/api/v1/dashboard/queries/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_diagnostic_statistics_success(self, client, auth_headers):
        """Test successfully getting diagnostic statistics."""
        response = client.get(
            "/api/v1/dashboard/diagnostics/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_diagnostics" in data
        assert "by_severity" in data

    def test_get_diagnostic_statistics_unauthorized(self, client):
        """Test getting diagnostic statistics without authentication."""
        response = client.get("/api/v1/dashboard/diagnostics/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.dashboard
class TestDashboardRecentActivity:
    """Test dashboard recent activity endpoints."""

    def test_get_recent_projects_success(self, client, auth_headers, test_project):
        """Test successfully getting recent projects."""
        response = client.get(
            "/api/v1/dashboard/projects/recent",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_recent_projects_unauthorized(self, client):
        """Test getting recent projects without authentication."""
        response = client.get("/api/v1/dashboard/projects/recent")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_recent_projects_pagination(self, client, auth_headers):
        """Test recent projects pagination."""
        response = client.get(
            "/api/v1/dashboard/projects/recent?limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) <= 5

    def test_get_recent_analyses_success(self, client, auth_headers, test_codebase):
        """Test successfully getting recent analyses."""
        response = client.get(
            "/api/v1/dashboard/analyses/recent",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_recent_analyses_unauthorized(self, client):
        """Test getting recent analyses without authentication."""
        response = client.get("/api/v1/dashboard/analyses/recent")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.dashboard
class TestDashboardTrends:
    """Test dashboard trends endpoints."""

    def test_get_query_trends_success(self, client, auth_headers):
        """Test successfully getting query trends."""
        response = client.get(
            "/api/v1/dashboard/queries/trends",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "trends" in data

    def test_get_query_trends_unauthorized(self, client):
        """Test getting query trends without authentication."""
        response = client.get("/api/v1/dashboard/queries/trends")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_diagnostic_trends_success(self, client, auth_headers):
        """Test successfully getting diagnostic trends."""
        response = client.get(
            "/api/v1/dashboard/diagnostics/trends",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "trends" in data

    def test_get_diagnostic_trends_unauthorized(self, client):
        """Test getting diagnostic trends without authentication."""
        response = client.get("/api/v1/dashboard/diagnostics/trends")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.dashboard
class TestDashboardTopIssues:
    """Test dashboard top issues endpoints."""

    def test_get_top_cost_queries_success(self, client, auth_headers):
        """Test successfully getting top cost queries."""
        response = client.get(
            "/api/v1/dashboard/queries/top-cost",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_top_cost_queries_unauthorized(self, client):
        """Test getting top cost queries without authentication."""
        response = client.get("/api/v1/dashboard/queries/top-cost")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_top_critical_diagnostics_success(self, client, auth_headers):
        """Test successfully getting top critical diagnostics."""
        response = client.get(
            "/api/v1/dashboard/diagnostics/critical",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_top_critical_diagnostics_unauthorized(self, client):
        """Test getting top critical diagnostics without authentication."""
        response = client.get("/api/v1/dashboard/diagnostics/critical")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.dashboard
class TestDashboardFilters:
    """Test dashboard filtering and search."""

    def test_dashboard_statistics_with_date_range(self, client, auth_headers):
        """Test dashboard statistics with date range filter."""
        response = client.get(
            "/api/v1/dashboard/overview?start_date=2024-01-01&end_date=2024-12-31",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_statistics_invalid_date_range(self, client, auth_headers):
        """Test dashboard statistics with invalid date range."""
        response = client.get(
            "/api/v1/dashboard/overview?start_date=invalid&end_date=invalid",
            headers=auth_headers
        )
        # Should either return 400 or 200 with empty data
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_dashboard_statistics_by_project(self, client, auth_headers, test_project):
        """Test dashboard statistics filtered by project."""
        response = client.get(
            f"/api/v1/dashboard/overview?project_id={test_project.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.dashboard
class TestDashboardEdgeCases:
    """Test dashboard edge cases."""

    def test_dashboard_with_no_data(self, client, auth_headers):
        """Test dashboard when user has no data."""
        # This would require a fresh user with no projects
        # For now, test that the endpoint returns successfully
        response = client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_large_dataset(self, client, auth_headers):
        """Test dashboard with large dataset."""
        # This would require creating many projects/codebases
        # Skip for now as it's a performance test
        pass

    def test_dashboard_concurrent_requests(self, client, auth_headers):
        """Test dashboard with concurrent requests."""
        # This would require async test execution
        # Skip for now
        pass


@pytest.mark.dashboard
class TestDashboardValidation:
    """Test dashboard data validation."""

    def test_dashboard_overview_data_structure(self, client, auth_headers):
        """Test dashboard overview returns correct data structure."""
        response = client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify expected fields
        expected_fields = [
            "total_projects",
            "total_codebases",
            "total_queries",
            "total_diagnostics",
            "critical_issues",
            "warning_issues"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    def test_dashboard_statistics_data_types(self, client, auth_headers):
        """Test dashboard statistics return correct data types."""
        response = client.get(
            "/api/v1/dashboard/projects/stats",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify data types
        assert isinstance(data.get("total_projects"), int)
        assert isinstance(data.get("active_projects"), int)

    def test_dashboard_pagination_limits(self, client, auth_headers):
        """Test dashboard pagination respects limits."""
        response = client.get(
            "/api/v1/dashboard/projects/recent?limit=100",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) <= 100

    def test_dashboard_negative_pagination(self, client, auth_headers):
        """Test dashboard pagination with negative values."""
        response = client.get(
            "/api/v1/dashboard/projects/recent?limit=-5",
            headers=auth_headers
        )
        # Should handle negative values gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
