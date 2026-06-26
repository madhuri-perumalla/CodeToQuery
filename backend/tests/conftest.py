"""Pytest configuration and shared fixtures."""
import os
import secrets
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User
from app.models.project import Project
from app.models.codebase import Codebase

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://codetoquery:codetoquery@localhost:5432/codetoquery_test"
)

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a test database session.

    Yields:
        Database session
    """
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a test client.

    Args:
        db: Database session fixture

    Yields:
        Test client
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db) -> User:
    """
    Create a test user.

    Args:
        db: Database session fixture

    Returns:
        User instance
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin_user(db) -> User:
    """
    Create a test admin user.

    Args:
        db: Database session fixture

    Returns:
        User instance
    """
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpassword123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user) -> dict:
    """
    Get authentication headers for a test user.

    Args:
        client: Test client fixture
        test_user: Test user fixture

    Returns:
        Dictionary with Authorization header
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client, test_admin_user) -> dict:
    """
    Get authentication headers for an admin user.

    Args:
        client: Test client fixture
        test_admin_user: Test admin user fixture

    Returns:
        Dictionary with Authorization header
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_admin_user.email,
            "password": "adminpassword123",
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_project(db, test_user) -> Project:
    """
    Create a test project.

    Args:
        db: Database session fixture
        test_user: Test user fixture

    Returns:
        Project instance
    """
    project = Project(
        owner_id=test_user.id,
        name="Test Project",
        description="A test project for integration testing",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture(scope="function")
def test_codebase(db, test_project) -> Codebase:
    """
    Create a test codebase.

    Args:
        db: Database session fixture
        test_project: Test project fixture

    Returns:
        Codebase instance
    """
    codebase = Codebase(
        project_id=test_project.id,
        scan_path="/tmp/test_codebase",
        status="completed",
        file_count=10,
    )
    db.add(codebase)
    db.commit()
    db.refresh(codebase)
    return codebase


@pytest.fixture(scope="session")
def test_secret_key() -> str:
    """
    Generate a test secret key for JWT tokens.

    Returns:
        Secret key string
    """
    return secrets.token_urlsafe(32)


@pytest.fixture(scope="function")
def sample_project_data() -> dict:
    """
    Sample project data for testing.

    Returns:
        Dictionary with project data
    """
    return {
        "name": "Sample Project",
        "description": "A sample project for testing",
    }


@pytest.fixture(scope="function")
def sample_codebase_data(test_project) -> dict:
    """
    Sample codebase data for testing.

    Args:
        test_project: Test project fixture

    Returns:
        Dictionary with codebase data
    """
    return {
        "project_id": test_project.id,
        "scan_path": "/tmp/sample_codebase",
    }


@pytest.fixture(scope="function")
def sample_user_data() -> dict:
    """
    Sample user data for testing.

    Returns:
        Dictionary with user data
    """
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
    }


@pytest.fixture(scope="function")
def invalid_auth_headers() -> dict:
    """
    Get invalid authentication headers.

    Returns:
        Dictionary with invalid Authorization header
    """
    return {"Authorization": "Bearer invalid_token"}
