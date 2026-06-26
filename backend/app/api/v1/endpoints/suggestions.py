"""Suggestions API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.models.codebase import Codebase
from app.models.diagnostic import Diagnostic
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery
from app.schemas.suggestion import (
    ApplySuggestionRequest,
    ApplySuggestionResponse,
    CodebaseSuggestionsResponse,
    FixSuggestionResponse,
    QuerySuggestionsResponse,
)
from app.services.suggestions import SuggestionService

router = APIRouter()


@router.post("/query/{query_id}", response_model=QuerySuggestionsResponse)
def generate_query_suggestions(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> QuerySuggestionsResponse:
    """
    Generate suggestions for a specific query.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query suggestions

    Raises:
        HTTPException: If query not found
    """
    query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found",
        )

    plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query_id).first()

    service = SuggestionService()
    suggestions = service.generate_suggestions_for_query(query, plan, db)

    return QuerySuggestionsResponse(
        query_id=query_id,
        index_recommendations=suggestions["index_recommendations"],
        rewrite_suggestions=suggestions["rewrite_suggestions"],
        filter_optimizations=suggestions["filter_optimizations"],
    )


@router.post("/diagnostic/{diagnostic_id}")
def generate_diagnostic_suggestions(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Generate suggestions for a diagnostic.

    Args:
        diagnostic_id: Diagnostic ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Generated suggestions

    Raises:
        HTTPException: If diagnostic not found
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic with id {diagnostic_id} not found",
        )

    service = SuggestionService()
    suggestions = service.generate_suggestions_for_diagnostic(diagnostic, db)

    # Save suggestions to database
    saved_suggestions = service.save_suggestions_to_db(diagnostic_id, suggestions, db)

    return {
        "diagnostic_id": diagnostic_id,
        "suggestions_generated": len(suggestions),
        "suggestions": [s.to_dict() for s in saved_suggestions],
    }


@router.get("/diagnostic/{diagnostic_id}")
def get_diagnostic_suggestions(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get suggestions for a diagnostic.

    Args:
        diagnostic_id: Diagnostic ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of suggestions

    Raises:
        HTTPException: If diagnostic not found
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnostic with id {diagnostic_id} not found",
        )

    service = SuggestionService()
    suggestions = service.get_suggestions_for_diagnostic(diagnostic_id, db)

    return {
        "diagnostic_id": diagnostic_id,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
    }


@router.get("")
def list_suggestions(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    List all suggestions with pagination.

    Args:
        codebase_id: Codebase ID (optional for global view)
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of suggestions
    """
    from app.models.suggestion import FixSuggestion as Suggestion

    # Build query
    query = db.query(Suggestion)

    # Filter by codebase_id if provided
    if codebase_id:
        query = query.join(Diagnostic, Suggestion.diagnostic_id == Diagnostic.id)\
                    .join(ExecutionPlanModel, Diagnostic.plan_id == ExecutionPlanModel.id)\
                    .join(ExtractedQuery, ExecutionPlanModel.query_id == ExtractedQuery.id)\
                    .filter(ExtractedQuery.codebase_id == codebase_id)

    # Get total count
    total = query.count()

    # Apply pagination
    skip = (page - 1) * page_size
    items = query.order_by(Suggestion.created_at.desc()).offset(skip).limit(page_size).all()

    return {
        "items": [
            {
                "id": suggestion.id,
                "diagnostic_id": suggestion.diagnostic_id,
                "suggestion_type": suggestion.suggestion_type,
                "description": suggestion.description,
                "impact": suggestion.impact,
                "effort": suggestion.effort,
                "priority": suggestion.priority,
                "status": suggestion.status,
                "created_at": suggestion.created_at.isoformat() if suggestion.created_at else None,
            }
            for suggestion in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/codebase/{codebase_id}", response_model=CodebaseSuggestionsResponse)
def get_codebase_suggestions(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseSuggestionsResponse:
    """
    Get all suggestions for a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Codebase suggestions

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )

    service = SuggestionService()
    suggestions = service.get_all_suggestions_for_codebase(codebase_id, db)

    return CodebaseSuggestionsResponse(
        codebase_id=codebase_id,
        total_suggestions=suggestions["total_suggestions"],
        high_impact_count=suggestions["high_impact_count"],
        suggestions_by_type=suggestions["suggestions_by_type"],
    )


@router.post("/apply", response_model=ApplySuggestionResponse)
def apply_suggestion(
    request: ApplySuggestionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ApplySuggestionResponse:
    """
    Apply a suggestion (mark as applied).

    Args:
        request: Apply suggestion request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Apply suggestion response

    Raises:
        HTTPException: If suggestion not found
    """
    service = SuggestionService()
    result = service.apply_suggestion(request.suggestion_id, db)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )

    return ApplySuggestionResponse(
        success=True,
        message="Suggestion applied successfully",
        suggestion=FixSuggestionResponse(**result) if result else None,
    )


@router.get("/high-impact")
def get_high_impact_suggestions(
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get high-impact suggestions for a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        High-impact suggestions

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )

    service = SuggestionService()
    all_suggestions = service.get_all_suggestions_for_codebase(codebase_id, db)

    # Filter for high impact suggestions
    high_impact = []
    for suggestion_type, suggestions in all_suggestions["suggestions_by_type"].items():
        for suggestion in suggestions:
            if suggestion.get("impact_estimate") == "high":
                high_impact.append(suggestion)

    return {
        "codebase_id": codebase_id,
        "total_high_impact": len(high_impact),
        "suggestions": high_impact,
    }


@router.get("/by-type/{suggestion_type}")
def get_suggestions_by_type(
    suggestion_type: str,
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get suggestions by type for a codebase.

    Args:
        suggestion_type: Suggestion type (add_index, rewrite_query, etc.)
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Suggestions by type

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )

    service = SuggestionService()
    all_suggestions = service.get_all_suggestions_for_codebase(codebase_id, db)

    suggestions = all_suggestions["suggestions_by_type"].get(suggestion_type, [])

    return {
        "codebase_id": codebase_id,
        "suggestion_type": suggestion_type,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
    }
