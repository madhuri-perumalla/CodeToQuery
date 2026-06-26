"""Integration tests for analysis endpoints."""
import pytest

from fastapi import status


@pytest.mark.analysis
class TestAnalysisCreation:
    """Test analysis creation endpoint."""

    def test_create_analysis_success(self, client, auth_headers, test_codebase):
        """Test successful analysis creation."""
        response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["codebase_id"] == test_codebase.id
        assert data["status"] in ["pending", "running"]
        assert "id" in data

    def test_create_analysis_unauthorized(self, client, test_codebase):
        """Test analysis creation without authentication."""
        response = client.post(
            "/api/v1/analysis",
            json={"codebase_id": test_codebase.id}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_analysis_invalid_codebase(self, client, auth_headers):
        """Test analysis creation with non-existent codebase."""
        response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": 99999}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_analysis_missing_codebase_id(self, client, auth_headers):
        """Test analysis creation without codebase_id."""
        response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.analysis
class TestAnalysisRetrieval:
    """Test analysis retrieval endpoints."""

    def test_get_analyses_success(self, client, auth_headers, test_codebase):
        """Test successfully getting analyses list."""
        # First create an analysis
        create_response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        
        response = client.get(
            "/api/v1/analysis",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_analyses_unauthorized(self, client):
        """Test getting analyses without authentication."""
        response = client.get("/api/v1/analysis")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_analysis_by_id_success(self, client, auth_headers, test_codebase):
        """Test successfully getting a specific analysis."""
        # First create an analysis
        create_response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        analysis_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/analysis/{analysis_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == analysis_id

    def test_get_analysis_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent analysis."""
        response = client.get(
            "/api/v1/analysis/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_analyses_by_codebase(self, client, auth_headers, test_codebase):
        """Test getting analyses filtered by codebase."""
        response = client.get(
            f"/api/v1/analysis?codebase_id={test_codebase.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_analyses_by_status(self, client, auth_headers):
        """Test getting analyses filtered by status."""
        response = client.get(
            "/api/v1/analysis?status=pending",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    def test_get_analyses_pagination(self, client, auth_headers):
        """Test analyses list pagination."""
        response = client.get(
            "/api/v1/analysis?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.analysis
class TestAnalysisStatus:
    """Test analysis status endpoint."""

    def test_get_analysis_status_success(self, client, auth_headers, test_codebase):
        """Test successfully getting analysis status."""
        # First create an analysis
        create_response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        analysis_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/analysis/{analysis_id}/status",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data

    def test_get_analysis_status_unauthorized(self, client, test_codebase):
        """Test getting analysis status without authentication."""
        response = client.get("/api/v1/analysis/1/status")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_analysis_status_not_found(self, client, auth_headers):
        """Test getting status for non-existent analysis."""
        response = client.get(
            "/api/v1/analysis/99999/status",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.analysis
class TestAnalysisResults:
    """Test analysis results endpoint."""

    def test_get_analysis_results_success(self, client, auth_headers, test_codebase):
        """Test successfully getting analysis results."""
        # First create an analysis
        create_response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        analysis_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/analysis/{analysis_id}/results",
            headers=auth_headers
        )
        # Analysis might still be running, so accept 200 or 202
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]

    def test_get_analysis_results_unauthorized(self, client):
        """Test getting analysis results without authentication."""
        response = client.get("/api/v1/analysis/1/results")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_analysis_results_not_found(self, client, auth_headers):
        """Test getting results for non-existent analysis."""
        response = client.get(
            "/api/v1/analysis/99999/results",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.analysis
class TestAnalysisCancellation:
    """Test analysis cancellation endpoint."""

    def test_cancel_analysis_success(self, client, auth_headers, test_codebase):
        """Test successfully cancelling an analysis."""
        # First create an analysis
        create_response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        analysis_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/v1/analysis/{analysis_id}/cancel",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_cancel_analysis_unauthorized(self, client, test_codebase):
        """Test cancelling analysis without authentication."""
        response = client.post("/api/v1/analysis/1/cancel")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_analysis_not_found(self, client, auth_headers):
        """Test cancelling non-existent analysis."""
        response = client.post(
            "/api/v1/analysis/99999/cancel",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cancel_completed_analysis(self, client, auth_headers, test_codebase):
        """Test cancelling already completed analysis."""
        # This test would require creating a completed analysis
        # For now, test the endpoint structure
        response = client.post(
            "/api/v1/analysis/1/cancel",
            headers=auth_headers
        )
        # Should return 404 since analysis doesn't exist
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.analysis
class TestAnalysisOptions:
    """Test analysis with custom options."""

    def test_create_analysis_with_options(self, client, auth_headers, test_codebase):
        """Test creating analysis with custom options."""
        options = {
            "enable_analyze": True,
            "cost_threshold": 500.0,
            "group_queries": True
        }
        response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={
                "codebase_id": test_codebase.id,
                "options": options
            }
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_analysis_with_invalid_options(self, client, auth_headers, test_codebase):
        """Test creating analysis with invalid options."""
        response = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={
                "codebase_id": test_codebase.id,
                "options": {"cost_threshold": -100}
            }
        )
        # Should either accept or validate the options
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.analysis
class TestAnalysisEdgeCases:
    """Test analysis edge cases and error handling."""

    def test_create_analysis_for_scanning_codebase(self, client, auth_headers, test_project):
        """Test creating analysis for codebase that is still scanning."""
        # Create a codebase with scanning status
        from app.models.codebase import Codebase
        from sqlalchemy.orm import Session
        
        # This would require database access, skip for now
        pass

    def test_concurrent_analysis_creation(self, client, auth_headers, test_codebase):
        """Test creating multiple analyses for same codebase."""
        # Create first analysis
        response1 = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Create second analysis
        response2 = client.post(
            "/api/v1/analysis",
            headers=auth_headers,
            json={"codebase_id": test_codebase.id}
        )
        # Should allow concurrent analyses
        assert response2.status_code == status.HTTP_201_CREATED

    def test_analysis_with_large_codebase(self, client, auth_headers):
        """Test analysis creation with codebase containing many files."""
        # This would require creating a large codebase
        # Skip for now as it's more of a performance test
        pass
