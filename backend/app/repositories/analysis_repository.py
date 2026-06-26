"""Analysis repository."""
from typing import Any, List

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.repositories.base_repository import BaseRepository


class AnalysisCreate(BaseModel):
    """Placeholder for analysis creation schema."""

    codebase_id: int


class AnalysisUpdate(BaseModel):
    """Placeholder for analysis update schema."""

    class Config:
        """Pydantic config."""

        extra = "allow"


class AnalysisRepository(BaseRepository[AnalysisRun, AnalysisCreate, AnalysisUpdate]):
    """Repository for AnalysisRun model."""

    def __init__(self) -> None:
        """Initialize analysis repository."""
        super().__init__(AnalysisRun)

    def get_by_codebase(
        self,
        db: Session,
        codebase_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AnalysisRun]:
        """
        Get analysis runs by codebase.

        Args:
            db: Database session
            codebase_id: Codebase ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AnalysisRun instances
        """
        return (
            db.query(AnalysisRun)
            .filter(AnalysisRun.codebase_id == codebase_id)
            .order_by(AnalysisRun.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_codebase(self, db: Session, codebase_id: int) -> AnalysisRun | None:
        """
        Get the latest analysis run for a codebase.

        Args:
            db: Database session
            codebase_id: Codebase ID

        Returns:
            AnalysisRun instance or None
        """
        return (
            db.query(AnalysisRun)
            .filter(AnalysisRun.codebase_id == codebase_id)
            .order_by(AnalysisRun.started_at.desc())
            .first()
        )

    def get_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AnalysisRun]:
        """
        Get analysis runs by status.

        Args:
            db: Database session
            status: Analysis status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AnalysisRun instances
        """
        return (
            db.query(AnalysisRun)
            .filter(AnalysisRun.status == status)
            .order_by(AnalysisRun.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
