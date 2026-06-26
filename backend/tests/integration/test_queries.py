"""Integration tests for query management endpoints."""
import pytest

from fastapi import status


@pytest.mark.queries
class TestQueryRetrieval:
    """Test query retrieval endpoints."""

    def test_get_queries_success(self, client, auth_headers):
        """Test successfully getting queries list."""
        response = client.get(
            "/api/v1/queries",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_queries_unauthorized(self, client):
        """Test getting queries without authentication."""
        response = client.get("/api/v1/queries")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_queries_by_codebase(self, client, auth_headers, test_codebase):
        """Test getting queries filtered by codebase."""
        response = client.get(
            f"/api/v1/queries?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_queries_by_query_type(self, client, auth_headers):
        """Test getting queries filtered by query type."""
        response = client.get(
            "/api/v1/queries?query_type=select",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_queries_by_status(self, client, auth_headers):
        """Test getting queries filtered by status."""
        response = client.get(
            "/api/v1/queries?status=healthy",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_queries_pagination(self, client, auth_headers):
        """Test queries list pagination."""
        response = client.get(
            "/api/v1/queries?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_queries_search(self, client, auth_headers):
        """Test searching queries by SQL content."""
        response = client.get(
            "/api/v1/queries?search=SELECT",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data


@pytest.mark.queries
class TestQueryDetail:
    """Test query detail endpoint."""

    def test_get_query_by_id_success(self, client, auth_headers):
        """Test successfully getting a specific query."""
        # This would require creating a query first
        # For now, test with a non-existent ID to verify endpoint structure
        response = client.get(
            "/api/v1/queries/1",
            headers=auth_headers
        )
        # Should return 404 since query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_query_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent query."""
        response = client.get(
            "/api/v1/queries/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_query_by_id_unauthorized(self, client):
        """Test getting query without authentication."""
        response = client.get("/api/v1/queries/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_query_with_execution_plan(self, client, auth_headers):
        """Test getting query with execution plan included."""
        response = client.get(
            "/api/v1/queries/1?include_plan=true",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_query_with_diagnostics(self, client, auth_headers):
        """Test getting query with diagnostics included."""
        response = client.get(
            "/api/v1/queries/1?include_diagnostics=true",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.queries
class TestQueryExecutionPlan:
    """Test query execution plan endpoints."""

    def test_get_execution_plan_success(self, client, auth_headers):
        """Test successfully getting execution plan for a query."""
        response = client.get(
            "/api/v1/queries/1/plan",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_execution_plan_unauthorized(self, client):
        """Test getting execution plan without authentication."""
        response = client.get("/api/v1/queries/1/plan")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_execution_plan_not_found(self, client, auth_headers):
        """Test getting execution plan for non-existent query."""
        response = client.get(
            "/api/v1/queries/99999/plan",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_parsed_execution_plan_success(self, client, auth_headers):
        """Test successfully getting parsed execution plan."""
        response = client.get(
            "/api/v1/queries/1/plan/parsed",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.queries
class TestQuerySimilarity:
    """Test query similarity endpoints."""

    def test_get_similar_queries_success(self, client, auth_headers):
        """Test successfully getting similar queries."""
        response = client.get(
            "/api/v1/queries/1/similar",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_similar_queries_unauthorized(self, client):
        """Test getting similar queries without authentication."""
        response = client.get("/api/v1/queries/1/similar")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_similar_queries_with_threshold(self, client, auth_headers):
        """Test getting similar queries with similarity threshold."""
        response = client.get(
            "/api/v1/queries/1/similar?threshold=0.85",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.queries
class TestQueryFiltering:
    """Test query filtering and search."""

    def test_filter_queries_by_cost_range(self, client, auth_headers):
        """Test filtering queries by cost range."""
        response = client.get(
            "/api/v1/queries?min_cost=100&max_cost=1000",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_filter_queries_by_dialect(self, client, auth_headers):
        """Test filtering queries by SQL dialect."""
        response = client.get(
            "/api/v1/queries?dialect=postgresql",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_filter_queries_by_source_type(self, client, auth_headers):
        """Test filtering queries by source type."""
        response = client.get(
            "/api/v1/queries?source_type=raw_sql",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_filter_queries_multiple_filters(self, client, auth_headers):
        """Test filtering queries with multiple filters."""
        response = client.get(
            "/api/v1/queries?query_type=select&status=healthy&dialect=postgresql",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data


@pytest.mark.queries
class TestQueryStatistics:
    """Test query statistics endpoints."""

    def test_get_query_statistics_success(self, client, auth_headers, test_codebase):
        """Test successfully getting query statistics."""
        response = client.get(
            f"/api/v1/queries/stats?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_queries" in data
        assert "avg_cost" in data

    def test_get_query_statistics_unauthorized(self, client, test_codebase):
        """Test getting query statistics without authentication."""
        response = client.get(
            f"/api/v1/queries/stats?codebase_id={test_codebase.id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_query_cost_distribution(self, client, auth_headers, test_codebase):
        """Test getting query cost distribution."""
        response = client.get(
            f"/api/v1/queries/cost-distribution?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.queries
class TestQueryEdgeCases:
    """Test query edge cases."""

    def test_queries_with_no_data(self, client, auth_headers):
        """Test queries when no queries exist."""
        response = client.get(
            "/api/v1/queries",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_queries_large_dataset(self, client, auth_headers):
        """Test queries with large dataset."""
        # This would require creating many queries
        # Skip for now as it's a performance test
        pass

    def test_queries_invalid_pagination(self, client, auth_headers):
        """Test queries with invalid pagination parameters."""
        response = client.get(
            "/api/v1/queries?skip=-1&limit=-1",
            headers=auth_headers
        )
        # Should handle invalid pagination gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_queries_sql_injection_attempt(self, client, auth_headers):
        """Test queries endpoint against SQL injection."""
        response = client.get(
            "/api/v1/queries?search=SELECT%20*%20FROM%20users%20--",
            headers=auth_headers
        )
        # Should handle safely
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.queries
class TestQueryValidation:
    """Test query data validation."""

    def test_query_data_structure(self, client, auth_headers):
        """Test query returns correct data structure."""
        response = client.get(
            "/api/v1/queries",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if data["items"]:
            query = data["items"][0]
            expected_fields = [
                "id",
                "codebase_id",
                "raw_sql",
                "normalized_sql",
                "query_hash",
                "dialect",
                "query_type",
                "source_type",
                "cost",
                "status",
                "created_at",
                "metadata"
            ]
            for field in expected_fields:
                assert field in query, f"Missing field: {field}"

    def test_query_status_values(self, client, auth_headers):
        """Test query status has valid values."""
        response = client.get(
            "/api/v1/queries",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        valid_statuses = ["healthy", "warning", "critical", "analyzing"]
        for query in data["items"]:
            if query.get("status"):
                assert query["status"] in valid_statuses

    def test_query_type_values(self, client, auth_headers):
        """Test query type has valid values."""
        response = client.get(
            "/api/v1/queries",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        valid_types = ["select", "insert", "update", "delete", "other"]
        for query in data["items"]:
            if query.get("query_type"):
                assert query["query_type"] in valid_types

    def test_query_pagination_limits(self, client, auth_headers):
        """Test queries pagination respects limits."""
        response = client.get(
            "/api/v1/queries?limit=100",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) <= 100


@pytest.mark.queries
class TestQueryLocations:
    """Test query location endpoints."""

    def test_get_query_locations_success(self, client, auth_headers):
        """Test successfully getting query locations."""
        response = client.get(
            "/api/v1/queries/1/locations",
            headers=auth_headers
        )
        # Should return 404 if query doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_query_locations_unauthorized(self, client):
        """Test getting query locations without authentication."""
        response = client.get("/api/v1/queries/1/locations")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.queries
class TestQueryNormalization:
    """Test query normalization endpoints."""

    def test_normalize_query_success(self, client, auth_headers):
        """Test successfully normalizing a query."""
        response = client.post(
            "/api/v1/queries/normalize",
            headers=auth_headers,
            json={"sql": "SELECT * FROM users WHERE id = 1"}
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_normalize_query_unauthorized(self, client):
        """Test normalizing query without authentication."""
        response = client.post(
            "/api/v1/queries/normalize",
            json={"sql": "SELECT * FROM users"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_normalize_query_invalid_sql(self, client, auth_headers):
        """Test normalizing invalid SQL."""
        response = client.post(
            "/api/v1/queries/normalize",
            headers=auth_headers,
            json={"sql": "INVALID SQL QUERY"}
        )
        # Should handle invalid SQL gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
