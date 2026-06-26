"""Groups API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.codebase import Codebase
from app.models.group import QueryGroup
from app.schemas.group import (
    GroupListResponse,
    GroupQueryResponse,
    GroupMemberSchema,
    QueryGroupResponse,
    RegroupRequest,
)
from app.services.grouping import PatternGroupingService

router = APIRouter()


@router.get("", response_model=GroupListResponse)
def list_groups(
    codebase_id: int | None = Query(None, description="Codebase ID (optional for global view)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    min_query_count: int | None = Query(None, description="Minimum query count filter"),
    sort_by: str = Query("query_count", description="Sort field"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> GroupListResponse:
    """
    List query groups.

    Args:
        codebase_id: Codebase ID (optional for global view)
        page: Page number
        page_size: Page size
        min_query_count: Minimum query count filter
        sort_by: Sort field
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of query groups

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
    
    # Build query
    query = db.query(QueryGroup)
    
    # Filter by codebase_id if provided
    if codebase_id:
        query = query.filter(QueryGroup.codebase_id == codebase_id)
    
    if min_query_count:
        query = query.filter(QueryGroup.query_count >= min_query_count)
    
    # Apply sorting
    if sort_by == "query_count":
        query = query.order_by(QueryGroup.query_count.desc())
    elif sort_by == "max_cost":
        query = query.order_by(QueryGroup.max_cost.desc())
    else:
        query = query.order_by(QueryGroup.created_at.desc())
    
    skip = (page - 1) * page_size
    items = query.offset(skip).limit(page_size).all()
    total = query.count()
    
    return GroupListResponse(
        items=[QueryGroupResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{group_id}", response_model=QueryGroupResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> QueryGroupResponse:
    """
    Get group details.

    Args:
        group_id: Group ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Group details

    Raises:
        HTTPException: If group not found
    """
    group = db.query(QueryGroup).filter(QueryGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )
    
    return QueryGroupResponse.model_validate(group)


@router.get("/{group_id}/queries")
def get_group_queries(
    group_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get queries in group.

    Args:
        group_id: Group ID
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Queries in group

    Raises:
        HTTPException: If group not found
    """
    group = db.query(QueryGroup).filter(QueryGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )
    
    skip = (page - 1) * page_size
    members = (
        db.query(group.members)
        .filter(group.members.group_id == group_id)
        .offset(skip)
        .limit(page_size)
        .all()
    )
    
    queries = []
    for member in members:
        if member.query:
            queries.append(
                GroupQueryResponse(
                    id=member.query.id,
                    similarity_score=float(member.similarity_score) if member.similarity_score else 0.0,
                    raw_sql=member.query.raw_sql,
                    normalized_sql=member.query.normalized_sql,
                    locations=[loc.to_dict() for loc in member.query.locations],
                )
            )
    
    total = db.query(group.members).filter(group.members.group_id == group_id).count()
    
    return {
        "items": queries,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/regroup", status_code=status.HTTP_202_ACCEPTED)
def regroup_queries(
    regroup_in: RegroupRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, str]:
    """
    Trigger regrouping.

    Args:
        regroup_in: Regrouping request data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Accepted response

    Raises:
        HTTPException: If codebase not found
    """
    # Verify codebase exists
    codebase = db.query(Codebase).filter(Codebase.id == regroup_in.codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {regroup_in.codebase_id} not found",
        )
    
    # TODO: Trigger background regrouping task
    # This will be implemented when grouping service is added

    return {"status": "accepted", "message": "Regrouping task started"}


# Pattern Grouping Endpoints

@router.post("/patterns/analyze")
def analyze_patterns(
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Analyze query patterns in a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Pattern analysis results

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

    service = PatternGroupingService()
    result = service.analyze_codebase_patterns(codebase_id, db)

    return result


@router.get("/patterns/inventory")
def get_pattern_inventory(
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get pattern inventory for a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Pattern inventory grouped by type

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

    service = PatternGroupingService()
    inventory = service.get_pattern_inventory(codebase_id, db)

    return inventory


@router.get("/patterns/high-risk")
def get_high_risk_patterns(
    codebase_id: int = Query(..., description="Codebase ID"),
    risk_threshold: float = Query(50.0, description="Minimum risk score"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get high-risk patterns above threshold.

    Args:
        codebase_id: Codebase ID
        risk_threshold: Minimum risk score
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of high-risk patterns

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

    service = PatternGroupingService()
    high_risk = service.get_high_risk_patterns(codebase_id, db, risk_threshold)

    return {
        "codebase_id": codebase_id,
        "risk_threshold": risk_threshold,
        "total_high_risk": len(high_risk),
        "patterns": high_risk,
    }


@router.get("/patterns/{pattern_id}")
def get_pattern_details(
    pattern_id: str,
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get details for a specific pattern.

    Args:
        pattern_id: Pattern ID
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Pattern details with matching queries

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

    service = PatternGroupingService()
    details = service.get_pattern_details(pattern_id, codebase_id, db)

    return details


@router.get("/patterns/{pattern_id}/files")
def get_pattern_files(
    pattern_id: str,
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get files impacted by a pattern.

    Args:
        pattern_id: Pattern ID
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        File impact information

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

    service = PatternGroupingService()
    file_impacts = service.get_files_impacted_by_pattern(pattern_id, codebase_id, db)

    return file_impacts


@router.get("/patterns/{pattern_id}/refactoring")
def get_refactoring_potential(
    pattern_id: str,
    codebase_id: int = Query(..., description="Codebase ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Calculate refactoring potential for a pattern.

    Args:
        pattern_id: Pattern ID
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Refactoring potential analysis

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

    service = PatternGroupingService()
    potential = service.calculate_refactoring_potential(pattern_id, codebase_id, db)

    return potential

