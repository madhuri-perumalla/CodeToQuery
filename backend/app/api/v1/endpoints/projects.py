"""Projects API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectStats,
    ProjectUpdate,
)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search term"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectListResponse:
    """
    List all projects.

    Args:
        page: Page number
        page_size: Page size
        search: Search term
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of projects
    """
    repo = ProjectRepository()
    skip = (page - 1) * page_size
    
    if search:
        # For search, we need to count the total results separately
        from sqlalchemy import or_
        search_query = db.query(Project).filter(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )
        total = search_query.count()
        items = search_query.offset(skip).limit(page_size).all()
    else:
        items = repo.get_multi(db, skip=skip, limit=page_size)
        total = repo.count(db)
    
    return ProjectListResponse(
        items=[ProjectResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectResponse:
    """
    Create a new project.

    Args:
        project_in: Project creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created project

    Raises:
        HTTPException: If project name already exists
    """
    repo = ProjectRepository()
    
    # Check if project name already exists
    existing = repo.get_by_name(db, project_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_in.name}' already exists",
        )
    
    try:
        # Add owner_id from current user
        project_data = project_in.model_dump()
        project_data['owner_id'] = current_user.get('sub') if isinstance(current_user, dict) else current_user.id
        project = repo.create(db, project_data)
        
        # Create codebase record if config contains codebase info
        if project_in.config and 'codebase' in project_in.config:
            from app.models.codebase import Codebase
            codebase_config = project_in.config['codebase']
            
            codebase = Codebase(
                project_id=project.id,
                scan_path=codebase_config.get('source', ''),
                status='pending',
                metadata={
                    'type': codebase_config.get('type', 'local'),
                    'extraction': project_in.config.get('extraction', {}),
                    'tech_stack': project_in.config.get('techStack', []),
                }
            )
            db.add(codebase)
            db.commit()
            db.refresh(codebase)
            
            # Trigger analysis run
            from app.models.analysis_run import AnalysisRun
            analysis = AnalysisRun(
                codebase_id=codebase.id,
                status='pending',
                metadata={'triggered_by': 'project_creation'},
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            # Trigger background analysis task
            try:
                from app.tasks.celery_app import celery_app
                celery_app.send_task('app.tasks.analysis_tasks.run_analysis_task', args=[analysis.id])
            except ImportError:
                # If Celery is not configured, analysis will need to be triggered manually
                pass
        
        return ProjectResponse.model_validate(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e


@router.get("/summary")
def get_projects_summary(
    project_id: int | None = Query(None, description="Project ID filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get projects summary statistics.

    Args:
        project_id: Optional project ID to filter by
        db: Database session
        current_user: Current authenticated user

    Returns:
        Projects summary statistics
    """
    try:
        from app.models.query import ExtractedQuery
        from app.models.codebase import Codebase
        from app.models.diagnostic import Diagnostic
        from app.models.execution_plan import ExecutionPlan
        from sqlalchemy import func
    except ImportError:
        # Models don't exist yet, return empty summary
        return {
            'totalQueries': 0,
            'totalProjects': 0,
            'totalCodebases': 0,
            'criticalIssues': 0,
            'highIssues': 0,
            'mediumIssues': 0,
            'lowIssues': 0,
            'avgQueryCost': 0,
            'maxQueryCost': 0,
            'mostExpensiveQueries': [],
            'topIssues': [],
            'recentAnalyses': [],
        }
    
    try:
        # Base queries
        projects_query = db.query(Project)
        codebases_query = db.query(Codebase)
        queries_query = db.query(ExtractedQuery)
        diagnostics_query = db.query(Diagnostic)
        
        # Filter by project if provided
        if project_id:
            projects_query = projects_query.filter(Project.id == project_id)
            codebases_query = codebases_query.filter(Codebase.project_id == project_id)
            try:
                queries_query = queries_query.join(Codebase).filter(Codebase.project_id == project_id)
            except Exception:
                queries_query = queries_query.filter(False)  # Return empty if join fails
            try:
                diagnostics_query = (
                    diagnostics_query
                    .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
                    .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
                    .join(Codebase, ExtractedQuery.codebase_id == Codebase.id)
                    .filter(Codebase.project_id == project_id)
                )
            except Exception:
                diagnostics_query = diagnostics_query.filter(False)  # Return empty if join fails
        
        # Calculate statistics
        total_projects = projects_query.count()
        total_codebases = codebases_query.count()
        total_queries = queries_query.count()
        
        # Diagnostic counts by severity
        critical_issues = diagnostics_query.filter(Diagnostic.severity == 'critical').count()
        high_issues = diagnostics_query.filter(Diagnostic.severity == 'high').count()
        medium_issues = diagnostics_query.filter(Diagnostic.severity == 'medium').count()
        low_issues = diagnostics_query.filter(Diagnostic.severity == 'low').count()
        
        # Cost statistics
        avg_query_cost = queries_query.with_entities(func.avg(ExtractedQuery.cost)).scalar() or 0
        max_query_cost = queries_query.with_entities(func.max(ExtractedQuery.cost)).scalar() or 0
        
        # Most expensive queries (top 5)
        most_expensive_queries = (
            queries_query
            .order_by(ExtractedQuery.cost.desc())
            .limit(5)
            .all()
        )
        
        # Top issues (recent critical/high diagnostics)
        top_issues = (
            diagnostics_query
            .filter(Diagnostic.severity.in_(['critical', 'high']))
            .order_by(Diagnostic.created_at.desc())
            .limit(10)
            .all()
        )
        
        # Recent analyses
        try:
            from app.models.analysis_run import AnalysisRun
            analyses_query = db.query(AnalysisRun)
            if project_id:
                analyses_query = (
                    analyses_query
                    .join(Codebase, AnalysisRun.codebase_id == Codebase.id)
                    .filter(Codebase.project_id == project_id)
                )
            
            recent_analyses = (
                analyses_query
                .order_by(AnalysisRun.created_at.desc())
                .limit(5)
                .all()
            )
        except Exception:
            recent_analyses = []
        
        return {
            'totalQueries': total_queries,
            'totalProjects': total_projects,
            'totalCodebases': total_codebases,
            'criticalIssues': critical_issues,
            'highIssues': high_issues,
            'mediumIssues': medium_issues,
            'lowIssues': low_issues,
            'avgQueryCost': float(avg_query_cost) if avg_query_cost else 0,
            'maxQueryCost': float(max_query_cost) if max_query_cost else 0,
            'mostExpensiveQueries': [
                {
                    'id': q.id,
                    'name': q.name or f'Query {q.id}',
                    'cost': float(q.cost) if q.cost else 0,
                    'rawSql': q.raw_sql[:200] + '...' if len(q.raw_sql) > 200 else q.raw_sql,
                }
                for q in most_expensive_queries
            ],
            'topIssues': [
                {
                    'id': d.id,
                    'severity': d.severity,
                    'message': d.message,
                    'createdAt': d.created_at.isoformat() if d.created_at else None,
                }
                for d in top_issues
            ],
            'recentAnalyses': [
                {
                    'id': a.id,
                    'projectId': a.codebase.project_id if a.codebase else None,
                    'codebaseId': a.codebase_id,
                    'status': a.status,
                    'startedAt': a.created_at.isoformat() if a.created_at else None,
                    'completedAt': a.updated_at.isoformat() if a.updated_at else None,
                    'queryCount': 0,  # TODO: Calculate actual query count
                    'issueCount': 0,  # TODO: Calculate actual issue count
                }
                for a in recent_analyses
            ],
        }
    except Exception as e:
        # Return empty summary on any error
        return {
            'totalQueries': 0,
            'totalProjects': 0,
            'totalCodebases': 0,
            'criticalIssues': 0,
            'highIssues': 0,
            'mediumIssues': 0,
            'lowIssues': 0,
            'avgQueryCost': 0,
            'maxQueryCost': 0,
            'mostExpensiveQueries': [],
            'topIssues': [],
            'recentAnalyses': [],
        }


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectResponse:
    """
    Get project details.

    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    repo = ProjectRepository()
    try:
        project = repo.get(db, project_id)
        return ProjectResponse.model_validate(project)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectResponse:
    """
    Update a project.

    Args:
        project_id: Project ID
        project_in: Project update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found or name conflict
    """
    repo = ProjectRepository()
    
    try:
        project = repo.get(db, project_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Check if name is being changed and if it conflicts
    if project_in.name and project_in.name != project.name:
        existing = repo.get_by_name(db, project_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project with name '{project_in.name}' already exists",
            )
    
    try:
        updated_project = repo.update(db, project, project_in)
        return ProjectResponse.model_validate(updated_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e


@router.get("/summary")
def get_projects_summary(
    project_id: int | None = Query(None, description="Project ID filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get projects summary statistics.

    Args:
        project_id: Optional project ID to filter by
        db: Database session
        current_user: Current authenticated user

    Returns:
        Projects summary statistics
    """
    try:
        from app.models.query import ExtractedQuery
        from app.models.codebase import Codebase
        from app.models.diagnostic import Diagnostic
        from app.models.execution_plan import ExecutionPlan
        from sqlalchemy import func
    except ImportError:
        # Models don't exist yet, return empty summary
        return {
            'totalQueries': 0,
            'totalProjects': 0,
            'totalCodebases': 0,
            'criticalIssues': 0,
            'highIssues': 0,
            'mediumIssues': 0,
            'lowIssues': 0,
            'avgQueryCost': 0,
            'maxQueryCost': 0,
            'mostExpensiveQueries': [],
            'topIssues': [],
            'recentAnalyses': [],
        }
    
    try:
        # Base queries
        projects_query = db.query(Project)
        codebases_query = db.query(Codebase)
        queries_query = db.query(ExtractedQuery)
        diagnostics_query = db.query(Diagnostic)
        
        # Filter by project if provided
        if project_id:
            projects_query = projects_query.filter(Project.id == project_id)
            codebases_query = codebases_query.filter(Codebase.project_id == project_id)
            try:
                queries_query = queries_query.join(Codebase).filter(Codebase.project_id == project_id)
            except Exception:
                queries_query = queries_query.filter(False)  # Return empty if join fails
            try:
                diagnostics_query = (
                    diagnostics_query
                    .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
                    .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
                    .join(Codebase, ExtractedQuery.codebase_id == Codebase.id)
                    .filter(Codebase.project_id == project_id)
                )
            except Exception:
                diagnostics_query = diagnostics_query.filter(False)  # Return empty if join fails
        
        # Calculate statistics
        total_projects = projects_query.count()
        total_codebases = codebases_query.count()
        total_queries = queries_query.count()
        
        # Diagnostic counts by severity
        critical_issues = diagnostics_query.filter(Diagnostic.severity == 'critical').count()
        high_issues = diagnostics_query.filter(Diagnostic.severity == 'high').count()
        medium_issues = diagnostics_query.filter(Diagnostic.severity == 'medium').count()
        low_issues = diagnostics_query.filter(Diagnostic.severity == 'low').count()
        
        # Cost statistics
        avg_query_cost = queries_query.with_entities(func.avg(ExtractedQuery.cost)).scalar() or 0
        max_query_cost = queries_query.with_entities(func.max(ExtractedQuery.cost)).scalar() or 0
        
        # Most expensive queries (top 5)
        most_expensive_queries = (
            queries_query
            .order_by(ExtractedQuery.cost.desc())
            .limit(5)
            .all()
        )
        
        # Top issues (recent critical/high diagnostics)
        top_issues = (
            diagnostics_query
            .filter(Diagnostic.severity.in_(['critical', 'high']))
            .order_by(Diagnostic.created_at.desc())
            .limit(10)
            .all()
        )
        
        # Recent analyses
        try:
            from app.models.analysis_run import AnalysisRun
            analyses_query = db.query(AnalysisRun)
            if project_id:
                analyses_query = (
                    analyses_query
                    .join(Codebase, AnalysisRun.codebase_id == Codebase.id)
                    .filter(Codebase.project_id == project_id)
                )
            
            recent_analyses = (
                analyses_query
                .order_by(AnalysisRun.created_at.desc())
                .limit(5)
                .all()
            )
        except Exception:
            recent_analyses = []
        
        return {
            'totalQueries': total_queries,
            'totalProjects': total_projects,
            'totalCodebases': total_codebases,
            'criticalIssues': critical_issues,
            'highIssues': high_issues,
            'mediumIssues': medium_issues,
            'lowIssues': low_issues,
            'avgQueryCost': float(avg_query_cost) if avg_query_cost else 0,
            'maxQueryCost': float(max_query_cost) if max_query_cost else 0,
            'mostExpensiveQueries': [
                {
                    'id': q.id,
                    'name': q.name or f'Query {q.id}',
                    'cost': float(q.cost) if q.cost else 0,
                    'rawSql': q.raw_sql[:200] + '...' if len(q.raw_sql) > 200 else q.raw_sql,
                }
                for q in most_expensive_queries
            ],
            'topIssues': [
                {
                    'id': d.id,
                    'severity': d.severity,
                    'message': d.message,
                    'createdAt': d.created_at.isoformat() if d.created_at else None,
                }
                for d in top_issues
            ],
            'recentAnalyses': [
                {
                    'id': a.id,
                    'projectId': a.codebase.project_id if a.codebase else None,
                    'codebaseId': a.codebase_id,
                    'status': a.status,
                    'startedAt': a.created_at.isoformat() if a.created_at else None,
                    'completedAt': a.updated_at.isoformat() if a.updated_at else None,
                    'queryCount': 0,  # TODO: Calculate actual query count
                    'issueCount': 0,  # TODO: Calculate actual issue count
                }
                for a in recent_analyses
            ],
        }
    except Exception as e:
        # Return empty summary on any error
        return {
            'totalQueries': 0,
            'totalProjects': 0,
            'totalCodebases': 0,
            'criticalIssues': 0,
            'highIssues': 0,
            'mediumIssues': 0,
            'lowIssues': 0,
            'avgQueryCost': 0,
            'maxQueryCost': 0,
            'mostExpensiveQueries': [],
            'topIssues': [],
            'recentAnalyses': [],
        }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    """
    Delete a project.

    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If project not found
    """
    repo = ProjectRepository()
    try:
        repo.delete(db, project_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{project_id}/stats", response_model=ProjectStats)
def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectStats:
    """
    Get project statistics.

    Args:
        project_id: Project ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Project statistics

    Raises:
        HTTPException: If project not found
    """
    repo = ProjectRepository()
    try:
        stats = repo.get_stats(db, project_id)
        return ProjectStats(**stats)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
