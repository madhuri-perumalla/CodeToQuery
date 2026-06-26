"""Integration tests for authentication endpoints."""
import pytest

from fastapi import status


@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_user_duplicate_email(self, client, test_user, sample_user_data):
        """Test registration with duplicate email fails."""
        sample_user_data["email"] = test_user.email
        response = client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_username(self, client, test_user, sample_user_data):
        """Test registration with duplicate username fails."""
        sample_user_data["username"] = test_user.username
        response = client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email format."""
        sample_user_data["email"] = "invalid-email"
        response = client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_weak_password(self, client, sample_user_data):
        """Test registration with weak password fails."""
        sample_user_data["password"] = "123"
        response = client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.auth
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful user login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.auth
class TestCurrentUser:
    """Test current user endpoint."""

    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test successfully getting current user."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["id"] == test_user.id

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client, invalid_auth_headers):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers=invalid_auth_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_malformed_token(self, client):
        """Test getting current user with malformed token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer malformed.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.auth
class TestTokenValidation:
    """Test JWT token validation."""

    def test_valid_token_access_protected_endpoint(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_expired_token(self, client):
        """Test accessing endpoint with expired token."""
        # This would require mocking time or using an old token
        # For now, test with invalid token format
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired.token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_without_bearer_prefix(self, client, auth_headers):
        """Test token without Bearer prefix."""
        token = auth_headers["Authorization"].replace("Bearer ", "")
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": token}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.auth
class TestPasswordChange:
    """Test password change functionality."""

    def test_change_password_success(self, client, auth_headers, test_user):
        """Test successful password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthorized(self, client):
        """Test password change without authentication."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test password change with weak new password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
