"""API dependencies."""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import NotFoundError, ValidationError
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.services.auth_service import AuthService

security = HTTPBearer()
settings = get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        User instance

    Raises:
        HTTPException: If authentication fails
    """
    # Skip authentication in development mode if no credentials provided
    if settings.DEBUG and not credentials:
        # Return a mock user for development
        try:
            user = db.query(User).first()
            if user:
                return user
            # Create a default development user if none exists
            user = User(
                email="dev@example.com",
                full_name="Development User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            # Return a dict-based mock user if User model fails
            return {"id": 1, "email": "dev@example.com", "sub": "1"}  # type: ignore
    
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    auth_service = AuthService()
    try:
        user = auth_service.get_current_user(db, user_id)
        return user
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> Project:
    """
    Get project by ID.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Project instance

    Raises:
        HTTPException: If project not found
    """
    try:
        repo = ProjectRepository()
        return repo.get(db, project_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
