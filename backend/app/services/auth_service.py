"""Authentication service."""
from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ConflictError, ValidationError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin

settings = get_settings()


class AuthService:
    """Service for authentication operations."""

    def __init__(self) -> None:
        """Initialize auth service."""
        self.user_repo = UserRepository()

    def register(self, db: Session, user_in: UserCreate) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            user_in: User creation data

        Returns:
            Created user

        Raises:
            ConflictError: If email or username already exists
        """
        # Check if email already exists
        existing_email = self.user_repo.get_by_email(db, user_in.email)
        if existing_email:
            raise ConflictError(
                "Email already registered",
                details={"field": "email", "value": user_in.email}
            )

        # Check if username already exists
        existing_username = self.user_repo.get_by_username(db, user_in.username)
        if existing_username:
            raise ConflictError(
                "Username already taken",
                details={"field": "username", "value": user_in.username}
            )

        # Create user
        user = self.user_repo.create(db, user_in)
        return user

    def authenticate(self, db: Session, credentials: UserLogin) -> Token:
        """
        Authenticate user and return access token.

        Args:
            db: Database session
            credentials: Login credentials

        Returns:
            Access token

        Raises:
            ValidationError: If credentials are invalid
        """
        # Get user by email or username
        user = self.user_repo.get_by_email_or_username(db, credentials.username)
        
        if not user:
            raise ValidationError(
                "Invalid credentials",
                details={"field": "username"}
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise ValidationError(
                "Invalid credentials",
                details={"field": "password"}
            )

        # Check if user is active
        if not user.is_active:
            raise ValidationError(
                "Account is inactive",
                details={"field": "is_active"}
            )

        # Update last login
        self.user_repo.update_last_login(db, user)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def get_current_user(self, db: Session, user_id: str) -> User:
        """
        Get current authenticated user.

        Args:
            db: Database session
            user_id: User ID from token

        Returns:
            User instance

        Raises:
            ValidationError: If user not found or inactive
        """
        user = self.user_repo.get(db, int(user_id))
        
        if not user:
            raise ValidationError(
                "User not found",
                details={"field": "user_id", "value": user_id}
            )

        if not user.is_active:
            raise ValidationError(
                "Account is inactive",
                details={"field": "is_active"}
            )

        return user

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """
        Verify JWT token and return payload.

        Args:
            token: JWT token

        Returns:
            Token payload or None if invalid
        """
        from app.core.security import decode_access_token

        return decode_access_token(token)
