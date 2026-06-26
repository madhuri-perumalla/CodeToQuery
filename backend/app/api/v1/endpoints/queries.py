"""Queries API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.codebase import Codebase
from app.models.query import ExtractedQuery
from app.repositories.query_repository import QueryRepository
from app.schemas.query import (
    QueryListResponse,
    QueryResponse,
    SimilarQueriesResponse,
)

router = APIRouter()


@router.get("", response_model=QueryListResponse)
def list_queries(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    query_type: str | None = Query(None, description="Query type filter"),
    source_type: str | None = Query(None, description="Source type filter"),
    severity: str | None = Query(None, description="Severity filter"),
    min_cost: float | None = Query(None, description="Minimum cost filter"),
    max_cost: float | None = Query(None, description="Maximum cost filter"),
    search: str | None = Query(None, description="Search term"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> QueryListResponse:
    """
    List queries with filters.

    Args:
        codebase_id: Codebase ID (optional for global view)
        page: Page number
        page_size: Page size
        query_type: Query type filter
        source_type: Source type filter
        severity: Severity filter
        min_cost: Minimum cost filter
        max_cost: Maximum cost filter
        search: Search term
        sort_by: Sort field
        sort_order: Sort order
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of queries

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
    
    repo = QueryRepository()
    skip = (page - 1) * page_size
    
    # Build filters
    filters: dict[str, Any] = {}
    if codebase_id:
        filters["codebase_id"] = codebase_id
    if query_type:
        filters["query_type"] = query_type
    if source_type:
        filters["source_type"] = source_type
    
    # Get queries
    if search:
        # For search, we need to count the total results separately
        from sqlalchemy import or_
        search_query = db.query(ExtractedQuery).filter(
            ExtractedQuery.codebase_id == codebase_id,
            or_(
                ExtractedQuery.raw_sql.ilike(f"%{search}%"),
                ExtractedQuery.normalized_sql.ilike(f"%{search}%")
            )
        )
        
        # Apply additional filters
        for key, value in filters.items():
            if key != "codebase_id" and hasattr(ExtractedQuery, key) and value is not None:
                search_query = search_query.filter(getattr(ExtractedQuery, key) == value)
        
        total = search_query.count()
        items = search_query.offset(skip).limit(page_size).all()
    else:
        items = repo.get_by_codebase(db, codebase_id=codebase_id, skip=skip, limit=page_size, **filters)
        total = repo.count(db, codebase_id=codebase_id, **filters)
    
    # Apply sorting
    if sort_by and hasattr(ExtractedQuery, sort_by):
        from sqlalchemy import desc, asc
        order_func = desc if sort_order == "desc" else asc
        if search:
            # For search, we need to apply sorting to the query
            items = search_query.order_by(order_func(getattr(ExtractedQuery, sort_by))).offset(skip).limit(page_size).all()
        else:
            # For non-search, we need to modify the repository call or apply sorting after
            # For now, apply simple sorting in Python (not ideal but functional)
            items.sort(key=lambda x: getattr(x, sort_by, 0), reverse=(sort_order == "desc"))
    
    return QueryListResponse(
        items=[QueryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> QueryResponse:
    """
    Get query details.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query details

    Raises:
        HTTPException: If query not found
    """
    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
        return QueryResponse.model_validate(query)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{query_id}/locations")
def get_query_locations(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get query code locations.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query locations

    Raises:
        HTTPException: If query not found
    """
    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
        return {"locations": [loc.to_dict() for loc in query.locations]}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{query_id}/plan")
def get_query_plan(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get execution plan.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Execution plan

    Raises:
        HTTPException: If query not found
    """
    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
        if not query.execution_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution plan for query {query_id} not found",
            )
        return query.execution_plan.to_dict()
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{query_id}/diagnostics")
def get_query_diagnostics(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get diagnostics for query.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query diagnostics

    Raises:
        HTTPException: If query not found
    """
    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
        if not query.execution_plan:
            return {"diagnostics": []}
        
        return {
            "diagnostics": [diag.to_dict() for diag in query.execution_plan.diagnostics],
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{query_id}/suggestions")
def get_query_suggestions(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get fix suggestions for query.

    Args:
        query_id: Query ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Fix suggestions

    Raises:
        HTTPException: If query not found
    """
    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
        if not query.execution_plan:
            return {"suggestions": []}
        
        suggestions = []
        for diag in query.execution_plan.diagnostics:
            suggestions.extend([sug.to_dict() for sug in diag.fix_suggestions])
        
        return {"suggestions": suggestions}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/similar", response_model=SimilarQueriesResponse)
def get_similar_queries(
    query_id: int = Query(..., description="Query ID"),
    threshold: float = Query(0.85, ge=0.0, le=1.0, description="Similarity threshold"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> SimilarQueriesResponse:
    """
    Find similar queries.

    Args:
        query_id: Query ID
        threshold: Similarity threshold
        limit: Maximum number of results
        db: Database session
        current_user: Current authenticated user

    Returns:
        Similar queries

    Raises:
        HTTPException: If query not found
    """
    from app.models.group import GroupMember
    from app.models.query import ExtractedQuery
    from sqlalchemy import and_

    repo = QueryRepository()
    try:
        query = repo.get(db, query_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Find queries in the same group with similarity above threshold
    similar_query_ids = (
        db.query(GroupMember.query_id)
        .join(GroupMember, and_(
            GroupMember.group_id == GroupMember.group_id,
            GroupMember.query_id != query_id
        ))
        .filter(
            GroupMember.query_id == query_id,
            GroupMember.similarity_score >= threshold
        )
        .limit(limit)
        .all()
    )
    
    similar_query_ids = [qid[0] for qid in similar_query_ids]
    
    if not similar_query_ids:
        # If no group members found, try to find queries with similar normalized SQL
        similar_queries = (
            db.query(ExtractedQuery)
            .filter(
                ExtractedQuery.id != query_id,
                ExtractedQuery.codebase_id == query.codebase_id,
                ExtractedQuery.normalized_sql.ilike(f"%{query.normalized_sql[:50]}%")
            )
            .limit(limit)
            .all()
        )
    else:
        similar_queries = (
            db.query(ExtractedQuery)
            .filter(ExtractedQuery.id.in_(similar_query_ids))
            .all()
        )
    
    return SimilarQueriesResponse(
        query_id=query_id,
        similar_queries=[
            {
                "id": q.id,
                "normalized_sql": q.normalized_sql,
                "similarity_score": 1.0,  # Default to 1.0 for now
                "cost": float(q.cost) if q.cost else None,
            }
            for q in similar_queries
        ],
    )
