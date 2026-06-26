"""Codebase schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CodebaseBase(BaseModel):
    """Base codebase schema."""

    project_id: int = Field(..., description="Project ID")
    scan_path: str = Field(..., min_length=1, max_length=1024, description="Codebase scan path")


class CodebaseCreate(CodebaseBase):
    """Schema for creating a codebase."""

    pass


class CodebaseResponse(CodebaseBase):
    """Schema for codebase response."""

    id: int
    scanned_at: datetime
    file_count: int
    status: str
    error_message: str | None
    metadata: dict[str, Any]

    class Config:
        """Pydantic config."""

        from_attributes = True


class CodebaseStatus(BaseModel):
    """Schema for codebase scan status."""

    status: str
    progress: int | None = None
    files_scanned: int | None = None
    queries_found: int | None = None
    current_file: str | None = None


class CodebaseFile(BaseModel):
    """Schema for codebase file."""

    file_path: str
    language: str | None = None
    size: int | None = None
    query_count: int = 0


class CodebaseFileListResponse(BaseModel):
    """Schema for codebase file list response."""

    items: list[CodebaseFile]
    total: int
    page: int
    page_size: int
