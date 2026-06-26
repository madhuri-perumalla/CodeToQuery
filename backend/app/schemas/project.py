"""Project schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    config: dict[str, Any] = Field(default_factory=dict, description="Project configuration")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    config: dict[str, Any] | None = Field(None, description="Project configuration")


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectStats(BaseModel):
    """Schema for project statistics."""

    total_codebases: int = 0
    total_queries: int = 0
    total_diagnostics: int = 0
    critical_issues: int = 0
    warning_issues: int = 0
    info_issues: int = 0
    avg_query_cost: float | None = None
    max_query_cost: float | None = None
    last_analysis: datetime | None = None


class ProjectListResponse(BaseModel):
    """Schema for project list response."""

    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
