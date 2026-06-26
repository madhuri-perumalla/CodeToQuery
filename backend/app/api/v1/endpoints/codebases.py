"""Codebases API endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.core.logging import get_logger
from app.models.codebase import Codebase
from app.repositories.project_repository import ProjectRepository
from app.schemas.codebase import (
    CodebaseCreate,
    CodebaseFile,
    CodebaseFileListResponse,
    CodebaseResponse,
    CodebaseStatus,
)
from app.tasks.extraction_task import run_extraction_task

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=list[CodebaseResponse])
def list_codebases(
    project_id: int | None = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[CodebaseResponse]:
    """
    List codebases.

    Args:
        project_id: Optional filter by project ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of codebases
    """
    query = db.query(Codebase)
    
    if project_id:
        query = query.filter(Codebase.project_id == project_id)
    
    codebases = query.all()
    return [CodebaseResponse.model_validate(codebase) for codebase in codebases]


@router.post("", response_model=CodebaseResponse, status_code=status.HTTP_201_CREATED)
def create_codebase(
    codebase_in: CodebaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseResponse:
    """
    Trigger codebase scan.

    Args:
        codebase_in: Codebase creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created codebase

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    project_repo = ProjectRepository()
    try:
        project_repo.get(db, codebase_in.project_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    
    # Create codebase record
    codebase = Codebase(
        project_id=codebase_in.project_id,
        scan_path=codebase_in.scan_path,
        status="pending",
    )
    db.add(codebase)
    db.commit()
    db.refresh(codebase)
    
    # Trigger background scanning task
    try:
        run_extraction_task.delay(codebase.id)
    except Exception as e:
        logger.error(f"Failed to trigger extraction task: {e}")
        # Don't fail the request if task triggering fails
        # The user can retry the scan later
    
    return CodebaseResponse.model_validate(codebase)


@router.get("/{codebase_id}", response_model=CodebaseResponse)
def get_codebase(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseResponse:
    """
    Get codebase details.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Codebase details

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    return CodebaseResponse.model_validate(codebase)


@router.get("/{codebase_id}/status", response_model=CodebaseStatus)
def get_codebase_status(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseStatus:
    """
    Get codebase scan status.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Codebase scan status

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    # Get metadata for progress information
    metadata = codebase.meta_data or {}
    
    return CodebaseStatus(
        status=codebase.status,
        progress=metadata.get("progress"),
        files_scanned=metadata.get("processed_files", codebase.file_count if codebase.status == "completed" else None),
        queries_found=metadata.get("total_queries"),
        current_file=metadata.get("current_file"),
    )


@router.post("/{codebase_id}/rescan", response_model=CodebaseResponse)
def rescan_codebase(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseResponse:
    """
    Trigger a re-scan of a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated codebase

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    # Reset status
    codebase.status = "pending"
    codebase.error_message = None
    db.commit()
    
    # Trigger background scanning task
    try:
        run_extraction_task.delay(codebase.id)
    except Exception as e:
        logger.error(f"Failed to trigger extraction task: {e}")
    
    return CodebaseResponse.model_validate(codebase)


@router.get("/{codebase_id}/files", response_model=CodebaseFileListResponse)
def get_codebase_files(
    codebase_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CodebaseFileListResponse:
    """
    List scanned files.

    Args:
        codebase_id: Codebase ID
        page: Page number
        page_size: Page size
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of files

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    # Get unique file paths from query locations
    from app.models.query import ExtractedQuery
    from app.models.location import QueryLocation
    
    # Query distinct file paths
    file_query = (
        db.query(QueryLocation.file_path)
        .join(ExtractedQuery, QueryLocation.query_id == ExtractedQuery.id)
        .filter(ExtractedQuery.codebase_id == codebase_id)
        .distinct()
    )
    
    total = file_query.count()
    skip = (page - 1) * page_size
    files = file_query.offset(skip).limit(page_size).all()
    
    # Get query count per file
    items = []
    for (file_path,) in files:
        query_count = (
            db.query(QueryLocation.id)
            .join(ExtractedQuery, QueryLocation.query_id == ExtractedQuery.id)
            .filter(
                ExtractedQuery.codebase_id == codebase_id,
                QueryLocation.file_path == file_path,
            )
            .count()
        )
        
        # Detect language from file extension
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".prisma": "prisma",
        }
        
        items.append(
            CodebaseFile(
                file_path=file_path,
                language=language_map.get(ext),
                query_count=query_count,
            )
        )
    
    return CodebaseFileListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{codebase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_codebase(
    codebase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    """
    Delete a codebase.

    Args:
        codebase_id: Codebase ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If codebase not found
    """
    codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
    if not codebase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Codebase with id {codebase_id} not found",
        )
    
    db.delete(codebase)
    db.commit()
