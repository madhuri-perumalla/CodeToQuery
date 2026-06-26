"""Normalization and duplicate detection API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.query import ExtractedQuery
from app.schemas.query import QueryResponse
from app.services.normalization import DuplicateDetector, StructuralComparison

router = APIRouter()


@router.post("/compare")
def compare_queries(
    sql1: str = Query(..., description="First SQL query"),
    sql2: str = Query(..., description="Second SQL query"),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Compare two SQL queries structurally.

    Args:
        sql1: First SQL query
        sql2: Second SQL query
        current_user: Current authenticated user

    Returns:
        Comparison result
    """
    comparator = StructuralComparison()
    result = comparator.compare(sql1, sql2)
    return result


@router.get("/{query_id}/similar")
def find_similar_queries(
    query_id: int,
    threshold: float = Query(0.85, ge=0.0, le=1.0, description="Similarity threshold"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Find structurally similar queries.

    Args:
        query_id: Query ID
        threshold: Similarity threshold
        limit: Maximum results
        db: Database session
        current_user: Current authenticated user

    Returns:
        Similar queries
    """
    # Get the query
    query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found",
        )

    # Get all queries from the same codebase
    all_queries = (
        db.query(ExtractedQuery)
        .filter(ExtractedQuery.codebase_id == query.codebase_id)
        .filter(ExtractedQuery.id != query_id)
        .all()
    )

    # Compare with all queries
    comparator = StructuralComparison()
    similar_queries = []

    for other_query in all_queries:
        comparison = comparator.compare(query.normalized_sql, other_query.normalized_sql)
        
        if comparison["similarity_score"] >= threshold:
            similar_queries.append({
                "id": other_query.id,
                "similarity_score": comparison["similarity_score"],
                "raw_sql": other_query.raw_sql,
                "normalized_sql": other_query.normalized_sql,
            })

    # Sort by similarity score
    similar_queries.sort(key=lambda x: x["similarity_score"], reverse=True)

    # Limit results
    similar_queries = similar_queries[:limit]

    return {
        "query_id": query_id,
        "threshold": threshold,
        "similar_queries": similar_queries,
    }


@router.get("/codebases/{codebase_id}/duplicates")
def get_duplicates(
    codebase_id: int,
    type: str = Query("exact", description="Duplicate type: exact, near, structural"),
    threshold: float = Query(0.85, ge=0.0, le=1.0, description="Similarity threshold for near/structural"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get duplicate queries for a codebase.

    Args:
        codebase_id: Codebase ID
        type: Duplicate type
        threshold: Similarity threshold
        db: Database session
        current_user: Current authenticated user

    Returns:
        Duplicate groups
    """
    detector = DuplicateDetector()

    if type == "exact":
        duplicates = detector.find_exact_duplicates(db, codebase_id)
    elif type == "near":
        duplicates = detector.find_near_duplicates(db, codebase_id, threshold)
    elif type == "structural":
        duplicates = detector.find_structural_duplicates(db, codebase_id, threshold)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid duplicate type: {type}",
        )

    return {
        "codebase_id": codebase_id,
        "type": type,
        "threshold": threshold,
        "duplicate_groups": duplicates,
    }


@router.get("/codebases/{codebase_id}/patterns")
def get_patterns(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get common query patterns for a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Query patterns
    """
    detector = DuplicateDetector()
    patterns = detector.detect_patterns(db, codebase_id)

    return {
        "codebase_id": codebase_id,
        "patterns": patterns,
    }


@router.get("/codebases/{codebase_id}/statistics")
def get_duplicate_statistics(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get duplicate detection statistics for a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Duplicate statistics
    """
    detector = DuplicateDetector()
    stats = detector.get_duplicate_statistics(db, codebase_id)

    return stats
