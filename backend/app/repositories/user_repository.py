"""User repository."""
from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model."""

    def __init__(self) -> None:
        """Initialize user repository."""
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User instance or None
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User instance or None
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(self, db: Session, identifier: str) -> User | None:
        """
        Get a user by email or username.

        Args:
            db: Database session
            identifier: Email or username

        Returns:
            User instance or None
        """
        return db.query(User).filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

    def update_last_login(self, db: Session, user: User) -> User:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user: User instance

        Returns:
            Updated user instance
        """
        from datetime import datetime

        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            obj_in: User creation schema

        Returns:
            Created user instance
        """
        from app.core.security import get_password_hash

        obj_in_data = obj_in.model_dump()
        password = obj_in_data.pop("password")
        hashed_password = get_password_hash(password)
        
        db_obj = User(**obj_in_data, hashed_password=hashed_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        """
        Update a user, hashing password if provided.

        Args:
            db: Database session
            db_obj: Existing user instance
            obj_in: Update schema or dictionary

        Returns:
            Updated user instance
        """
        from app.core.security import get_password_hash

        if isinstance(obj_in, UserUpdate):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj
