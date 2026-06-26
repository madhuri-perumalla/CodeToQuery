"""Query schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryLocationSchema(BaseModel):
    """Schema for query location."""

    id: int
    file_path: str
    line_number: int
    column_number: int
    function_name: str | None
    class_name: str | None
    context_snippet: str | None
    call_stack: list[dict[str, Any]]

    class Config:
        """Pydantic config."""

        from_attributes = True


class ExecutionPlanSchema(BaseModel):
    """Schema for execution plan."""

    id: int
    query_id: int
    plan_json: dict[str, Any]
    plan_hash: str | None
    total_cost: float | None
    total_rows: float | None
    plan_width: int | None
    format: str
    analyzed_at: datetime
    execution_time_ms: float | None
    metadata: dict[str, Any]

    class Config:
        """Pydantic config."""

        from_attributes = True


class DiagnosticSchema(BaseModel):
    """Schema for diagnostic."""

    id: int
    plan_id: int
    rule_id: str
    severity: str
    message: str
    location: dict[str, Any] | None
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FixSuggestionSchema(BaseModel):
    """Schema for fix suggestion."""

    id: int
    diagnostic_id: int
    suggestion_type: str
    description: str
    sql_change: str | None
    impact_estimate: str | None
    confidence_score: float | None
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class QueryResponse(BaseModel):
    """Schema for query response."""

    id: int
    codebase_id: int
    raw_sql: str
    normalized_sql: str
    query_hash: str
    dialect: str
    query_type: str | None
    source_type: str | None
    created_at: datetime
    metadata: dict[str, Any]
    execution_plan: ExecutionPlanSchema | None = None
    diagnostics: list[DiagnosticSchema] = []
    locations: list[QueryLocationSchema] = []

    class Config:
        """Pydantic config."""

        from_attributes = True


class QueryListResponse(BaseModel):
    """Schema for query list response."""

    items: list[QueryResponse]
    total: int
    page: int
    page_size: int


class SimilarQuerySchema(BaseModel):
    """Schema for similar query."""

    id: int
    similarity_score: float
    raw_sql: str
    locations: list[QueryLocationSchema]


class SimilarQueriesResponse(BaseModel):
    """Schema for similar queries response."""

    query_id: int
    similar_queries: list[SimilarQuerySchema]
