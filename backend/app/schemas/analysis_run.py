"""Analysis run schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    """Schema for creating an analysis run."""

    codebase_id: int = Field(..., description="Codebase ID")
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Analysis options (enable_analyze, cost_threshold, group_queries)",
    )


class AnalysisResponse(BaseModel):
    """Schema for analysis run response."""

    id: int
    codebase_id: int
    status: str
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None
    metadata: dict[str, Any]

    class Config:
        """Pydantic config."""

        from_attributes = True


class AnalysisStatus(BaseModel):
    """Schema for analysis status."""

    status: str
    progress: int | None = None
    queries_analyzed: int | None = None
    diagnostics_found: int | None = None
    current_step: str | None = None


class AnalysisSummary(BaseModel):
    """Schema for analysis summary."""

    total_queries: int
    queries_with_plans: int
    total_diagnostics: int
    critical_count: int
    warning_count: int
    info_count: int


class TopIssue(BaseModel):
    """Schema for top issue."""

    query_id: int
    severity: str
    message: str
    cost: float | None


class AnalysisResults(BaseModel):
    """Schema for analysis results."""

    analysis_id: int
    summary: AnalysisSummary
    top_issues: list[TopIssue]


class DiagnosticListResponse(BaseModel):
    """Schema for diagnostic list response."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
