"""Diagnostics API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.models.codebase import Codebase
from app.models.diagnostic import Diagnostic
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.schemas.diagnostic import (
    DiagnosticListResponse,
    DiagnosticResponse,
    DiagnosticSummary,
)
from app.services.diagnostics import CodeAwareDiagnosticsService, rule_engine

router = APIRouter()


@router.get("", response_model=DiagnosticListResponse)
def list_diagnostics(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    severity: str | None = Query(None, description="Severity filter"),
    rule_id: str | None = Query(None, description="Rule ID filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DiagnosticListResponse:
    """
    List all diagnostics with filters.

    Args:
        codebase_id: Codebase ID (optional for global view)
        severity: Severity filter
        rule_id: Rule ID filter
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of diagnostics

    Raises:
        HTTPException: If codebase not found
    """
    # If codebase_id is provided, verify it exists
    if codebase_id:
        codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
        if not codebase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Codebase with id {codebase_id} not found",
            )
    
    # Build query - need to join with execution_plans and extracted_queries
    from app.models.execution_plan import ExecutionPlan
    from app.models.query import ExtractedQuery
    
    query = (
        db.query(Diagnostic)
        .join(ExecutionPlan, Diagnostic.plan_id == ExecutionPlan.id)
        .join(ExtractedQuery, ExecutionPlan.query_id == ExtractedQuery.id)
    )
    
    # Filter by codebase_id if provided
    if codebase_id:
        query = query.filter(ExtractedQuery.codebase_id == codebase_id)
    
    if severity:
        query = query.filter(Diagnostic.severity == severity)
    
    if rule_id:
        query = query.filter(Diagnostic.rule_id == rule_id)
    
    query = query.order_by(Diagnostic.created_at.desc())
    
    skip = (page - 1) * page_size
    items = query.offset(skip).limit(page_size).all()
    total = query.count()
    
    return DiagnosticListResponse(
        items=[DiagnosticResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{diagnostic_id}", response_model=DiagnosticResponse)
def get_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DiagnosticResponse:
    """
    Get diagnostic details.

    Args:
        diagnostic_id: Diagnostic ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Diagnostic details

    Raises:
        HTTPException: If diagnostic not found
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic with id {diagnostic_id} not found",
        )
    
    return DiagnosticResponse.model_validate(diagnostic)


@router.get("/{diagnostic_id}/suggestions")
def get_diagnostic_suggestions(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get suggestions for diagnostic.

    Args:
        diagnostic_id: Diagnostic ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Fix suggestions

    Raises:
        HTTPException: If diagnostic not found
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic with id {diagnostic_id} not found",
        )
    
    suggestions = [sug.to_dict() for sug in diagnostic.fix_suggestions]
    
    return {"suggestions": suggestions}


@router.get("/summary", response_model=DiagnosticSummary)
def get_diagnostic_summary(
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DiagnosticSummary:
    """
    Get diagnostic summary.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Diagnostic summary

    Raises:
        HTTPException: If codebase not found
    """
    # Verify codebase exists
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    # TODO: Implement actual summary calculation
    # This is a placeholder implementation
    return DiagnosticSummary(
        codebase_id=codebase_id,
        total_diagnostics=0,
        by_severity={"critical": 0, "warning": 0, "info": 0},
        by_rule={},
        top_rules=[],
    )


# Rule Engine Endpoints

@router.get("/rules")
def list_rules(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    List all registered diagnostic rules.

    Args:
        current_user: Current authenticated user

    Returns:
        List of rules with status
    """
    status_dict = rule_engine.get_rule_status()
    return {"rules": status_dict}


@router.get("/rules/{rule_id}")
def get_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get a specific rule.

    Args:
        rule_id: Rule identifier
        current_user: Current authenticated user

    Returns:
        Rule details

    Raises:
        HTTPException: If rule not found
    """
    rule = rule_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found",
        )

    return {
        "rule_id": rule.rule_id,
        "severity": rule.severity,
        "enabled": rule.check_enabled(),
    }


@router.post("/rules/{rule_id}/enable")
def enable_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Enable a diagnostic rule.

    Args:
        rule_id: Rule identifier
        current_user: Current authenticated user

    Returns:
        Updated rule status

    Raises:
        HTTPException: If rule not found
    """
    try:
        rule_engine.enable_rule(rule_id)
        return {"rule_id": rule_id, "enabled": True}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post("/rules/{rule_id}/disable")
def disable_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Disable a diagnostic rule.

    Args:
        rule_id: Rule identifier
        current_user: Current authenticated user

    Returns:
        Updated rule status

    Raises:
        HTTPException: If rule not found
    """
    try:
        rule_engine.disable_rule(rule_id)
        return {"rule_id": rule_id, "enabled": False}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post("/plans/{plan_id}/evaluate")
def evaluate_plan(
    plan_id: int,
    rule_ids: list[str] | None = Query(None, description="Specific rules to evaluate"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Evaluate diagnostic rules against an execution plan.

    Args:
        plan_id: Execution plan ID
        rule_ids: Specific rules to evaluate (None = all)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Diagnostic results

    Raises:
        HTTPException: If plan not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    results = rule_engine.evaluate_all(plan.plan_json, rule_ids)

    return {
        "plan_id": plan_id,
        "total_results": len(results),
        "results": [result.to_dict() for result in results],
    }


@router.post("/plans/{plan_id}/evaluate/{rule_id}")
def evaluate_plan_rule(
    plan_id: int,
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Evaluate a specific rule against an execution plan.

    Args:
        plan_id: Execution plan ID
        rule_id: Rule identifier
        db: Database session
        current_user: Current authenticated user

    Returns:
        Diagnostic results

    Raises:
        HTTPException: If plan or rule not found
    """
    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution plan with id {plan_id} not found",
        )

    try:
        results = rule_engine.evaluate_rule(rule_id, plan.plan_json)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return {
        "plan_id": plan_id,
        "rule_id": rule_id,
        "total_results": len(results),
        "results": [result.to_dict() for result in results],
    }


# Code-Aware Diagnostics Endpoints

@router.post("/plans/{plan_id}/code-aware")
def get_code_aware_diagnostics(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get code-aware diagnostics for an execution plan.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Code-aware diagnostics with source context

    Raises:
        HTTPException: If plan not found
    """
    service = CodeAwareDiagnosticsService()
    diagnostics = service.generate_code_aware_diagnostics(plan_id, db)

    return {
        "plan_id": plan_id,
        "total_diagnostics": len(diagnostics),
        "diagnostics": [d.to_dict() for d in diagnostics],
    }


@router.post("/queries/{query_id}/code-aware")
def get_code_aware_diagnostics_for_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get code-aware diagnostics for a query.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Code-aware diagnostics with source context

    Raises:
        HTTPException: If query not found
    """
    service = CodeAwareDiagnosticsService()
    diagnostics = service.generate_code_aware_diagnostics_for_query(query_id, db)

    return {
        "query_id": query_id,
        "total_diagnostics": len(diagnostics),
        "diagnostics": [d.to_dict() for d in diagnostics],
    }


@router.post("/codebases/{codebase_id}/code-aware")
def get_code_aware_diagnostics_for_codebase(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get code-aware diagnostics for all queries in a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Code-aware diagnostics grouped by file

    Raises:
        HTTPException: If codebase not found
    """
    # Verify codebase exists
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )

    service = CodeAwareDiagnosticsService()
    result = service.generate_code_aware_diagnostics_for_codebase(codebase_id, db)

    return result


@router.get("/plans/{plan_id}/source-context")
def get_source_context_for_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get source context for an execution plan.

    Args:
        plan_id: Execution plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Source context

    Raises:
        HTTPException: If plan not found
    """
    service = CodeAwareDiagnosticsService()
    source_context = service.get_source_context_for_plan(plan_id, db)

    if not source_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source context not found for plan {plan_id}",
        )

    return {
        "plan_id": plan_id,
        "source_context": source_context.to_dict(),
    }


@router.get("/queries/{query_id}/source-context")
def get_source_context_for_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get source context for a query.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Source context

    Raises:
        HTTPException: If query not found or no source context
    """
    service = CodeAwareDiagnosticsService()
    source_context = service.get_source_context_for_query(query_id, db)

    if not source_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source context not found for query {query_id}",
        )

    return {
        "query_id": query_id,
        "source_context": source_context.to_dict(),
    }


