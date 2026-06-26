"""EXPLAIN analysis API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import AnalysisError, NotFoundError
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery
from app.schemas.analysis_run import AnalysisCreate
from app.services.explain import ExecutionPlanParser, ExplainService

router = APIRouter()


@router.post("/queries/{query_id}/explain")
def explain_query(
    query_id: int,
    analyze: bool = Query(False, description="Use ANALYZE for actual execution time"),
    timeout: int = Query(30, description="Query timeout in seconds"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Run EXPLAIN on a query.

    Args:
        query_id: Query ID
        analyze: Whether to use ANALYZE
        timeout: Query timeout
        db: Database session
        current_user: Current authenticated user

    Returns:
        Execution plan result

    Raises:
        HTTPException: If query not found or analysis fails
    """
    # Get query
    query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found",
        )

    try:
        explain_service = ExplainService()
        execution_plan = explain_service.analyze_query(
            query_id,
            db,
            analyze=analyze,
            timeout=timeout,
        )

        return {
            "query_id": query_id,
            "plan_id": execution_plan.id,
            "total_cost": float(execution_plan.total_cost) if execution_plan.total_cost else None,
            "total_rows": float(execution_plan.total_rows) if execution_plan.total_rows else None,
            "plan_width": execution_plan.plan_width,
            "execution_time_ms": float(execution_plan.execution_time_ms) if execution_plan.execution_time_ms else None,
            "analyzed": execution_plan.meta_data.get("analyzed", False),
            "plan_json": execution_plan.plan_json,
        }

    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/plans")
def list_execution_plans(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    List execution plans with pagination.

    Args:
        codebase_id: Codebase ID (optional for global view)
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of execution plans
    """
    from app.models.query import ExtractedQuery

    # Build query
    query = db.query(ExecutionPlanModel).join(ExtractedQuery, ExecutionPlanModel.query_id == ExtractedQuery.id)

    # Filter by codebase_id if provided
    if codebase_id:
        query = query.filter(ExtractedQuery.codebase_id == codebase_id)

    # Get total count
    total = query.count()

    # Apply pagination
    skip = (page - 1) * page_size
    items = query.order_by(ExecutionPlanModel.analyzed_at.desc()).offset(skip).limit(page_size).all()

    return {
        "items": [
            {
                "id": plan.id,
                "query_id": plan.query_id,
                "total_cost": float(plan.total_cost) if plan.total_cost else None,
                "total_rows": float(plan.total_rows) if plan.total_rows else None,
                "plan_width": plan.plan_width,
                "execution_time_ms": float(plan.execution_time_ms) if plan.execution_time_ms else None,
                "analyzed_at": plan.analyzed_at.isoformat() if plan.analyzed_at else None,
                "format": plan.format,
            }
            for plan in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/plans/{plan_id}")
def get_execution_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get execution plan details.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Execution plan details

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    return {
        "id": plan.id,
        "query_id": plan.query_id,
        "plan_json": plan.plan_json,
        "plan_hash": plan.plan_hash,
        "total_cost": float(plan.total_cost) if plan.total_cost else None,
        "total_rows": float(plan.total_rows) if plan.total_rows else None,
        "plan_width": plan.plan_width,
        "format": plan.format,
        "analyzed_at": plan.analyzed_at.isoformat() if plan.analyzed_at else None,
        "execution_time_ms": float(plan.execution_time_ms) if plan.execution_time_ms else None,
        "metadata": plan.meta_data,
    }


@router.get("/plans/{plan_id}/parsed")
def get_parsed_execution_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get parsed execution plan with structured nodes.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Parsed execution plan

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    # Parse execution plan
    parser = ExecutionPlanParser()
    execution_plan = parser.parse(plan.plan_json)

    return execution_plan.to_dict()


@router.get("/plans/{plan_id}/nodes/{node_type}")
def get_nodes_by_type(
    plan_id: int,
    node_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get nodes of a specific type from execution plan.

    Args:
        plan_id: Execution plan ID
        node_type: Node type to find
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of matching nodes

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    # Parse execution plan
    parser = ExecutionPlanParser()
    execution_plan = parser.parse(plan.plan_json)

    # Find nodes by type
    nodes = parser.find_nodes_by_type(execution_plan, node_type)

    return {
        "plan_id": plan_id,
        "node_type": node_type,
        "count": len(nodes),
        "nodes": [node.to_dict() for node in nodes],
    }


@router.get("/plans/{plan_id}/statistics")
def get_plan_statistics(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get execution plan statistics.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Plan statistics

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    # Parse execution plan
    parser = ExecutionPlanParser()
    execution_plan = parser.parse(plan.plan_json)

    # Get statistics
    statistics = parser.get_plan_statistics(execution_plan)

    return {
        "plan_id": plan_id,
        **statistics,
    }


@router.get("/plans/{plan_id}/summary")
def get_plan_summary(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get execution plan summary.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Plan summary

    Raises:
        HTTPException: If plan not found
    """
    explain_service = ExplainService()

    try:
        summary = explain_service.get_plan_summary(plan_id, db)
        return summary
    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/plans/{plan_id}/issues")
def get_plan_issues(
    plan_id: int,
    cost_threshold: float = Query(1000.0, description="Cost threshold for expensive nodes"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get issues detected in execution plan.

    Args:
        plan_id: Execution plan ID
        cost_threshold: Cost threshold
        db: Database session
        current_user: Current authenticated user

    Returns:
        Detected issues

    Raises:
        HTTPException: If plan not found
    """
    explain_service = ExplainService()

    try:
        issues = explain_service.detect_issues(plan_id, db, cost_threshold)
        return issues
    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post("/batch")
def explain_batch(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Run EXPLAIN on multiple queries.

    Args:
        analysis_in: Analysis creation data (codebase_id, options)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Batch analysis results

    Raises:
        HTTPException: If codebase not found
    """
    # Get queries from codebase
    from app.models.codebase import Codebase

    codebase = db.query(Codebase).filter(Codebase.id == analysis_in.codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {analysis_in.codebase_id} not found",
        )

    # Get all queries from codebase
    queries = (
        db.query(ExtractedQuery)
        .filter(ExtractedQuery.codebase_id == codebase.id)
        .all()
    )

    query_ids = [q.id for q in queries]

    if not query_ids:
        return {
            "codebase_id": codebase.id,
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

    explain_service = ExplainService()
    analyze = analysis_in.options.get("enable_analyze", False)
    timeout = analysis_in.options.get("explain_timeout", 30)

    results = explain_service.analyze_batch(query_ids, db, analyze=analyze, timeout=timeout)

    return {
        "codebase_id": codebase.id,
        **results,
    }
