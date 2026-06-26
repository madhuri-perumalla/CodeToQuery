"""Project repository."""
from typing import Any, List

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.base_repository import BaseRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """Repository for Project model."""

    def __init__(self) -> None:
        """Initialize project repository."""
        super().__init__(Project)

    def get_by_name(self, db: Session, name: str) -> Project | None:
        """
        Get a project by name.

        Args:
            db: Database session
            name: Project name

        Returns:
            Project instance or None
        """
        return db.query(Project).filter(Project.name == name).first()

    def get_with_codebases(self, db: Session, id: int) -> Project:
        """
        Get a project with codebases.

        Args:
            db: Database session
            id: Project ID

        Returns:
            Project instance with codebases
        """
        return db.query(Project).filter(Project.id == id).first()

    def search(self, db: Session, search: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Search projects by name or description.

        Args:
            db: Database session
            search: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Project instances
        """
        return (
            db.query(Project)
            .filter(
                (Project.name.ilike(f"%{search}%")) | (Project.description.ilike(f"%{search}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_stats(self, db: Session, id: int) -> dict[str, Any]:
        """
        Get project statistics.

        Args:
            db: Database session
            id: Project ID

        Returns:
            Dictionary with project statistics
        """
        from app.models.codebase import Codebase
        from app.models.query import ExtractedQuery
        from app.models.diagnostic import Diagnostic
        from app.models.execution_plan import ExecutionPlan
        from app.models.analysis_run import AnalysisRun
        from sqlalchemy import func

        project = self.get(db, id)
        
        # Get all codebases for this project
        codebase_ids = [cb.id for cb in project.codebases] if project.codebases else []
        
        if not codebase_ids:
            return {
                "total_codebases": 0,
                "total_queries": 0,
                "total_diagnostics": 0,
                "critical_issues": 0,
                "warning_issues": 0,
                "info_issues": 0,
                "avg_query_cost": None,
                "max_query_cost": None,
                "last_analysis": None,
            }
        
        # Count queries
        total_queries = db.query(ExtractedQuery).filter(
            ExtractedQuery.codebase_id.in_(codebase_ids)
        ).count()
        
        # Count diagnostics by severity
        diagnostics_query = (
            db.query(Diagnostic)
            .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
            .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
            .filter(ExtractedQuery.codebase_id.in_(codebase_ids))
        )
        
        critical_issues = diagnostics_query.filter(Diagnostic.severity == 'critical').count()
        high_issues = diagnostics_query.filter(Diagnostic.severity == 'high').count()
        medium_issues = diagnostics_query.filter(Diagnostic.severity == 'medium').count()
        low_issues = diagnostics_query.filter(Diagnostic.severity == 'low').count()
        info_issues = diagnostics_query.filter(Diagnostic.severity == 'info').count()
        
        total_diagnostics = critical_issues + high_issues + medium_issues + low_issues + info_issues
        
        # Calculate cost statistics
        cost_stats = db.query(
            func.avg(ExtractedQuery.cost),
            func.max(ExtractedQuery.cost)
        ).filter(
            ExtractedQuery.codebase_id.in_(codebase_ids),
            ExtractedQuery.cost.isnot(None)
        ).first()
        
        avg_query_cost = float(cost_stats[0]) if cost_stats and cost_stats[0] else None
        max_query_cost = float(cost_stats[1]) if cost_stats and cost_stats[1] else None
        
        # Get last analysis run
        last_analysis = (
            db.query(AnalysisRun)
            .filter(AnalysisRun.codebase_id.in_(codebase_ids))
            .order_by(AnalysisRun.created_at.desc())
            .first()
        )
        
        return {
            "total_codebases": len(codebase_ids),
            "total_queries": total_queries,
            "total_diagnostics": total_diagnostics,
            "critical_issues": critical_issues,
            "warning_issues": high_issues,
            "info_issues": info_issues,
            "avg_query_cost": avg_query_cost,
            "max_query_cost": max_query_cost,
            "last_analysis": last_analysis.created_at.isoformat() if last_analysis and last_analysis.created_at else None,
        }
