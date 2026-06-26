"""Analysis API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.analysis_run import AnalysisRun
from app.models.codebase import Codebase
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis_run import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisResults,
    AnalysisStatus,
    DiagnosticListResponse,
)

router = APIRouter()


@router.get("")
def list_analysis_runs(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    List analysis runs with pagination.

    Args:
        codebase_id: Codebase ID (optional for global view)
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of analysis runs
    """
    # Build query
    query = db.query(AnalysisRun)

    # Filter by codebase_id if provided
    if codebase_id:
        query = query.filter(AnalysisRun.codebase_id == codebase_id)

    # Get total count
    total = query.count()

    # Apply pagination
    skip = (page - 1) * page_size
    items = query.order_by(AnalysisRun.started_at.desc()).offset(skip).limit(page_size).all()

    return {
        "items": [
            {
                "id": analysis.id,
                "codebase_id": analysis.codebase_id,
                "status": analysis.status,
                "started_at": analysis.started_at.isoformat() if analysis.started_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "error_message": analysis.error_message,
            }
            for analysis in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AnalysisResponse:
    """
    Trigger analysis run.

    Args:
        analysis_in: Analysis creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created analysis run

    Raises:
        HTTPException: If codebase not found
    """
    # Verify codebase exists
    codebase = db.query(Codebase).filter(Codebase.id == analysis_in.codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {analysis_in.codebase_id} not found",
        )
    
    # Create analysis run record
    analysis = AnalysisRun(
        codebase_id=analysis_in.codebase_id,
        status="pending",
        metadata={"options": analysis_in.options},
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Trigger background analysis task
    try:
        from app.tasks.celery_app import celery_app
        from app.tasks.analysis_tasks import run_analysis_task
        celery_app.send_task('app.tasks.analysis_tasks.run_analysis_task', args=[analysis.id])
    except ImportError:
        # If Celery is not configured, run analysis synchronously
        from app.tasks.analysis_tasks import run_analysis_task
        try:
            # Create a mock DatabaseTask for synchronous execution
            class SyncDatabaseTask:
                _db = db
                @property
                def db(self):
                    return self._db
            sync_task = SyncDatabaseTask()
            run_analysis_task(sync_task, analysis.id)
        except Exception as e:
            analysis.status = "failed"
            analysis.error_message = str(e)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Synchronous analysis failed: {str(e)}"
            )
    
    return AnalysisResponse.model_validate(analysis)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AnalysisResponse:
    """
    Get analysis run details.

    Args:
        analysis_id: Analysis run ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Analysis run details

    Raises:
        HTTPException: If analysis run not found
    """
    repo = AnalysisRepository()
    try:
        analysis = repo.get(db, analysis_id)
        return AnalysisResponse.model_validate(analysis)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{analysis_id}/status", response_model=AnalysisStatus)
def get_analysis_status(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AnalysisStatus:
    """
    Get analysis status.

    Args:
        analysis_id: Analysis run ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Analysis status

    Raises:
        HTTPException: If analysis run not found
    """
    from app.models.query import ExtractedQuery
    from app.models.diagnostic import Diagnostic
    from app.models.execution_plan import ExecutionPlan
    from sqlalchemy import func

    repo = AnalysisRepository()
    try:
        analysis = repo.get(db, analysis_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Calculate actual progress and statistics
    codebase = db.query(Codebase).filter(Codebase.id == analysis.codebase_id).first()
    if not codebase:
        return AnalysisStatus(
            status=analysis.status,
            progress=0,
            queries_analyzed=0,
            diagnostics_found=0,
            current_step="initialization",
        )
    
    # Count queries analyzed for this codebase
    queries_analyzed = db.query(ExtractedQuery).filter(
        ExtractedQuery.codebase_id == analysis.codebase_id,
        ExtractedQuery.created_at >= analysis.started_at
    ).count()
    
    # Count diagnostics found
    diagnostics_found = (
        db.query(Diagnostic)
        .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
        .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
        .filter(
            ExtractedQuery.codebase_id == analysis.codebase_id,
            ExtractedQuery.created_at >= analysis.started_at
        )
        .count()
    )
    
    # Estimate progress based on status
    progress_map = {
        "pending": 0,
        "running": 50,
        "completed": 100,
        "failed": 0,
        "cancelled": 0,
    }
    
    step_map = {
        "pending": "queued",
        "running": "analyzing",
        "completed": "finished",
        "failed": "error",
        "cancelled": "cancelled",
    }
    
    return AnalysisStatus(
        status=analysis.status,
        progress=progress_map.get(analysis.status, 0),
        queries_analyzed=queries_analyzed,
        diagnostics_found=diagnostics_found,
        current_step=step_map.get(analysis.status, "unknown"),
    )


@router.get("/{analysis_id}/results", response_model=AnalysisResults)
def get_analysis_results(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AnalysisResults:
    """
    Get analysis results.

    Args:
        analysis_id: Analysis run ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Analysis results

    Raises:
        HTTPException: If analysis run not found
    """
    repo = AnalysisRepository()
    try:
        analysis = repo.get(db, analysis_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Calculate actual results
    from app.models.query import ExtractedQuery
    from app.models.diagnostic import Diagnostic
    from app.models.execution_plan import ExecutionPlan
    from app.core.config import get_settings
    from app.schemas.analysis_run import AnalysisSummary, TopIssue
    from sqlalchemy import func

    if analysis.status != "completed":
        return AnalysisResults(
            analysis_id=analysis_id,
            summary=AnalysisSummary(
                total_queries=0,
                queries_with_plans=0,
                total_diagnostics=0,
                critical_count=0,
                warning_count=0,
                info_count=0,
            ),
            top_issues=[],
        )
    
    settings = get_settings()
    cost_threshold = settings.DEFAULT_COST_THRESHOLD
    
    # Count queries analyzed
    total_queries = db.query(ExtractedQuery).filter(
        ExtractedQuery.codebase_id == analysis.codebase_id,
        ExtractedQuery.created_at >= analysis.started_at
    ).count()
    
    # Count queries with plans
    queries_with_plans = (
        db.query(ExtractedQuery)
        .join(ExecutionPlan, ExecutionPlan.query_id == ExtractedQuery.id)
        .filter(
            ExtractedQuery.codebase_id == analysis.codebase_id,
            ExtractedQuery.created_at >= analysis.started_at
        )
        .count()
    )
    
    # Count diagnostics by severity
    diagnostics_query = (
        db.query(Diagnostic)
        .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
        .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
        .filter(
            ExtractedQuery.codebase_id == analysis.codebase_id,
            ExtractedQuery.created_at >= analysis.started_at
        )
    )
    
    total_diagnostics = diagnostics_query.count()
    critical_count = diagnostics_query.filter(Diagnostic.severity == 'critical').count()
    warning_count = diagnostics_query.filter(Diagnostic.severity == 'warning').count()
    info_count = diagnostics_query.filter(Diagnostic.severity == 'info').count()
    
    # Get top issues
    top_diagnostics = (
        diagnostics_query
        .order_by(Diagnostic.created_at.desc())
        .limit(10)
        .all()
    )
    
    top_issues = [
        TopIssue(
            id=d.id,
            severity=d.severity,
            message=d.message,
            plan_id=d.plan_id,
        )
        for d in top_diagnostics
    ]
    
    return AnalysisResults(
        analysis_id=analysis_id,
        summary=AnalysisSummary(
            total_queries=total_queries,
            queries_with_plans=queries_with_plans,
            total_diagnostics=total_diagnostics,
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
        ),
        top_issues=top_issues,
    )


@router.get("/{analysis_id}/diagnostics", response_model=DiagnosticListResponse)
def get_analysis_diagnostics(
    analysis_id: int,
    severity: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DiagnosticListResponse:
    """
    Get all diagnostics from analysis run.

    Args:
        analysis_id: Analysis run ID
        severity: Severity filter
        limit: Maximum number of results
        db: Database session
        current_user: Current authenticated user

    Returns:
        Diagnostics from analysis run

    Raises:
        HTTPException: If analysis run not found
    """
    repo = AnalysisRepository()
    try:
        analysis = repo.get(db, analysis_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Retrieve actual diagnostics
    from app.models.query import ExtractedQuery
    from app.models.diagnostic import Diagnostic
    from app.models.execution_plan import ExecutionPlan
    from app.schemas.diagnostic import DiagnosticResponse

    diagnostics_query = (
        db.query(Diagnostic)
        .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
        .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
        .filter(
            ExtractedQuery.codebase_id == analysis.codebase_id,
            ExtractedQuery.created_at >= analysis.started_at
        )
    )
    
    if severity:
        diagnostics_query = diagnostics_query.filter(Diagnostic.severity == severity)
    
    total = diagnostics_query.count()
    diagnostics = diagnostics_query.limit(limit).all()
    
    return DiagnosticListResponse(
        items=[DiagnosticResponse.model_validate(d) for d in diagnostics],
        total=total,
        page=1,
        page_size=limit,
    )
