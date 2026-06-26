"""Query repository."""
from typing import Any, List

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.models.query import ExtractedQuery
from app.repositories.base_repository import BaseRepository


class QueryCreate(BaseModel):
    """Placeholder for query creation schema."""

    raw_sql: str
    normalized_sql: str
    query_hash: str
    codebase_id: int


class QueryUpdate(BaseModel):
    """Placeholder for query update schema."""

    class Config:
        """Pydantic config."""

        extra = "allow"


class QueryRepository(BaseRepository[ExtractedQuery, QueryCreate, QueryUpdate]):
    """Repository for ExtractedQuery model."""

    def __init__(self) -> None:
        """Initialize query repository."""
        super().__init__(ExtractedQuery)

    def get_by_hash(self, db: Session, query_hash: str) -> ExtractedQuery | None:
        """
        Get a query by hash.

        Args:
            db: Database session
            query_hash: Query hash

        Returns:
            ExtractedQuery instance or None
        """
        return db.query(ExtractedQuery).filter(ExtractedQuery.query_hash == query_hash).first()

    def get_by_codebase(
        self,
        db: Session,
        codebase_id: int,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ExtractedQuery]:
        """
        Get queries by codebase with filtering.

        Args:
            db: Database session
            codebase_id: Codebase ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filter criteria

        Returns:
            List of ExtractedQuery instances
        """
        query = db.query(ExtractedQuery).filter(ExtractedQuery.codebase_id == codebase_id)
        
        for key, value in filters.items():
            if hasattr(ExtractedQuery, key) and value is not None:
                query = query.filter(getattr(ExtractedQuery, key) == value)
        
        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        codebase_id: int,
        search: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExtractedQuery]:
        """
        Search queries by SQL content.

        Args:
            db: Database session
            codebase_id: Codebase ID
            search: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ExtractedQuery instances
        """
        return (
            db.query(ExtractedQuery)
            .filter(
                ExtractedQuery.codebase_id == codebase_id,
                (ExtractedQuery.raw_sql.ilike(f"%{search}%"))
                | (ExtractedQuery.normalized_sql.ilike(f"%{search}%")),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_relations(self, db: Session, id: int) -> ExtractedQuery:
        """
        Get a query with all relations.

        Args:
            db: Database session
            id: Query ID

        Returns:
            ExtractedQuery instance with relations
        """
        return db.query(ExtractedQuery).filter(ExtractedQuery.id == id).first()
