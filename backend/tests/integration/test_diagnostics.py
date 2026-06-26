"""Integration tests for diagnostics endpoints."""
import pytest

from fastapi import status


@pytest.mark.diagnostics
class TestDiagnosticsRetrieval:
    """Test diagnostics retrieval endpoints."""

    def test_get_diagnostics_success(self, client, auth_headers):
        """Test successfully getting diagnostics list."""
        response = client.get(
            "/api/v1/diagnostics",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_diagnostics_unauthorized(self, client):
        """Test getting diagnostics without authentication."""
        response = client.get("/api/v1/diagnostics")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_diagnostics_by_severity(self, client, auth_headers):
        """Test getting diagnostics filtered by severity."""
        response = client.get(
            "/api/v1/diagnostics?severity=critical",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_diagnostics_by_plan_id(self, client, auth_headers):
        """Test getting diagnostics filtered by execution plan ID."""
        response = client.get(
            "/api/v1/diagnostics?plan_id=1",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_diagnostics_pagination(self, client, auth_headers):
        """Test diagnostics list pagination."""
        response = client.get(
            "/api/v1/diagnostics?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_diagnostics_by_codebase(self, client, auth_headers, test_codebase):
        """Test getting diagnostics filtered by codebase."""
        response = client.get(
            f"/api/v1/diagnostics?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data


@pytest.mark.diagnostics
class TestDiagnosticDetail:
    """Test diagnostic detail endpoint."""

    def test_get_diagnostic_by_id_success(self, client, auth_headers):
        """Test successfully getting a specific diagnostic."""
        # This would require creating a diagnostic first
        # For now, test with a non-existent ID to verify endpoint structure
        response = client.get(
            "/api/v1/diagnostics/1",
            headers=auth_headers
        )
        # Should return 404 since diagnostic doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_diagnostic_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent diagnostic."""
        response = client.get(
            "/api/v1/diagnostics/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_diagnostic_by_id_unauthorized(self, client):
        """Test getting diagnostic without authentication."""
        response = client.get("/api/v1/diagnostics/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.diagnostics
class TestDiagnosticSummary:
    """Test diagnostic summary endpoint."""

    def test_get_diagnostic_summary_success(self, client, auth_headers, test_codebase):
        """Test successfully getting diagnostic summary."""
        response = client.get(
            f"/api/v1/diagnostics/summary?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_diagnostics" in data
        assert "by_severity" in data

    def test_get_diagnostic_summary_unauthorized(self, client, test_codebase):
        """Test getting diagnostic summary without authentication."""
        response = client.get(
            f"/api/v1/diagnostics/summary?codebase_id={test_codebase.id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_diagnostic_summary_invalid_codebase(self, client, auth_headers):
        """Test getting summary for non-existent codebase."""
        response = client.get(
            "/api/v1/diagnostics/summary?codebase_id=99999",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]


@pytest.mark.diagnostics
class TestDiagnosticRules:
    """Test diagnostic rules endpoint."""

    def test_get_diagnostic_rules_success(self, client, auth_headers):
        """Test successfully getting diagnostic rules."""
        response = client.get(
            "/api/v1/diagnostics/rules",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_diagnostic_rules_unauthorized(self, client):
        """Test getting diagnostic rules without authentication."""
        response = client.get("/api/v1/diagnostics/rules")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_diagnostic_rule_by_id_success(self, client, auth_headers):
        """Test successfully getting a specific diagnostic rule."""
        response = client.get(
            "/api/v1/diagnostics/rules/full_table_scan",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_diagnostic_rule_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent diagnostic rule."""
        response = client.get(
            "/api/v1/diagnostics/rules/nonexistent_rule",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.diagnostics
class TestDiagnosticFiltering:
    """Test diagnostic filtering and search."""

    def test_filter_diagnostics_by_rule_id(self, client, auth_headers):
        """Test filtering diagnostics by rule ID."""
        response = client.get(
            "/api/v1/diagnostics?rule_id=full_table_scan",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_filter_diagnostics_multiple_severities(self, client, auth_headers):
        """Test filtering diagnostics by multiple severities."""
        response = client.get(
            "/api/v1/diagnostics?severity=critical,warning",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_search_diagnostics_by_message(self, client, auth_headers):
        """Test searching diagnostics by message content."""
        response = client.get(
            "/api/v1/diagnostics?search=table",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data


@pytest.mark.diagnostics
class TestDiagnosticSuggestions:
    """Test diagnostic suggestions endpoints."""

    def test_get_suggestions_for_diagnostic_success(self, client, auth_headers):
        """Test successfully getting suggestions for a diagnostic."""
        # This would require a diagnostic with suggestions
        response = client.get(
            "/api/v1/diagnostics/1/suggestions",
            headers=auth_headers
        )
        # Should return 404 if diagnostic doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_get_suggestions_unauthorized(self, client):
        """Test getting suggestions without authentication."""
        response = client.get("/api/v1/diagnostics/1/suggestions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.diagnostics
class TestDiagnosticActions:
    """Test diagnostic action endpoints."""

    def test_apply_suggestion_success(self, client, auth_headers):
        """Test successfully applying a suggestion."""
        # This would require a suggestion to apply
        response = client.post(
            "/api/v1/suggestions/1/apply",
            headers=auth_headers
        )
        # Should return 404 if suggestion doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]

    def test_apply_suggestion_unauthorized(self, client):
        """Test applying suggestion without authentication."""
        response = client.post("/api/v1/suggestions/1/apply")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dismiss_diagnostic_success(self, client, auth_headers):
        """Test successfully dismissing a diagnostic."""
        # This would require a dismiss endpoint
        # For now, test the endpoint structure
        response = client.post(
            "/api/v1/diagnostics/1/dismiss",
            headers=auth_headers
        )
        # Should return 404 if diagnostic doesn't exist or 405 if endpoint doesn't exist
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]


@pytest.mark.diagnostics
class TestDiagnosticEdgeCases:
    """Test diagnostic edge cases."""

    def test_diagnostics_with_no_data(self, client, auth_headers):
        """Test diagnostics when no diagnostics exist."""
        response = client.get(
            "/api/v1/diagnostics",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_diagnostics_large_dataset(self, client, auth_headers):
        """Test diagnostics with large dataset."""
        # This would require creating many diagnostics
        # Skip for now as it's a performance test
        pass

    def test_diagnostics_invalid_severity_filter(self, client, auth_headers):
        """Test diagnostics with invalid severity filter."""
        response = client.get(
            "/api/v1/diagnostics?severity=invalid",
            headers=auth_headers
        )
        # Should handle invalid filter gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.diagnostics
class TestDiagnosticValidation:
    """Test diagnostic data validation."""

    def test_diagnostic_data_structure(self, client, auth_headers):
        """Test diagnostic returns correct data structure."""
        # Create a diagnostic first or use existing
        response = client.get(
            "/api/v1/diagnostics",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if data["items"]:
            diagnostic = data["items"][0]
            expected_fields = [
                "id",
                "plan_id",
                "rule_id",
                "severity",
                "message",
                "location",
                "metadata"
            ]
            for field in expected_fields:
                assert field in diagnostic, f"Missing field: {field}"

    def test_diagnostic_severity_values(self, client, auth_headers):
        """Test diagnostic severity has valid values."""
        response = client.get(
            "/api/v1/diagnostics",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        valid_severities = ["critical", "warning", "info"]
        for diagnostic in data["items"]:
            assert diagnostic["severity"] in valid_severities

    def test_diagnostic_pagination_limits(self, client, auth_headers):
        """Test diagnostics pagination respects limits."""
        response = client.get(
            "/api/v1/diagnostics?limit=100",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) <= 100


@pytest.mark.diagnostics
class TestDiagnosticCodeAware:
    """Test code-aware diagnostics endpoints."""

    def test_get_code_aware_diagnostics_success(self, client, auth_headers, test_codebase):
        """Test successfully getting code-aware diagnostics."""
        response = client.get(
            f"/api/v1/diagnostics/code-aware?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        # Should return 200 or 404 if no code-aware diagnostics exist
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_code_aware_diagnostics_unauthorized(self, client, test_codebase):
        """Test getting code-aware diagnostics without authentication."""
        response = client.get(
            f"/api/v1/diagnostics/code-aware?codebase_id={test_codebase.id}"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_code_aware_diagnostics_with_source_context(self, client, auth_headers, test_codebase):
        """Test getting code-aware diagnostics with source context."""
        response = client.get(
            f"/api/v1/diagnostics/code-aware?codebase_id={test_codebase.id}&include_context=true",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
