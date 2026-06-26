"""Base repository with common CRUD operations."""
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType]) -> None:
        """
        Initialize base repository.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: int) -> ModelType:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise NotFoundError(self.model.__name__, id)
        return obj

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Filter criteria

        Returns:
            List of model instances
        """
        query = db.query(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, **filters: Any) -> int:
        """
        Count records with filtering.

        Args:
            db: Database session
            **filters: Filter criteria

        Returns:
            Count of records
        """
        query = db.query(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Creation schema

        Returns:
            Created model instance
        """
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Update schema or dictionary

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> ModelType:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Deleted model instance

        Raises:
            NotFoundError: If record not found
        """
        obj = self.get(db, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, **filters: Any) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            **filters: Filter criteria

        Returns:
            True if record exists, False otherwise
        """
        query = db.query(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        
        return query.first() is not None
