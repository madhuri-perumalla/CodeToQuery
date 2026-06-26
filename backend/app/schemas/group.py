"""Group schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryGroupResponse(BaseModel):
    """Schema for query group response."""

    id: int
    codebase_id: int
    name: str
    pattern_signature: str
    query_count: int
    max_cost: float | None
    avg_cost: float | None
    total_cost: float | None
    similarity_threshold: float | None
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class GroupMemberSchema(BaseModel):
    """Schema for group member."""

    id: int
    group_id: int
    query_id: int
    similarity_score: float
    is_representative: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class GroupQueryResponse(BaseModel):
    """Schema for group query response."""

    id: int
    similarity_score: float
    raw_sql: str
    normalized_sql: str
    locations: list[dict[str, Any]]


class GroupListResponse(BaseModel):
    """Schema for group list response."""

    items: list[QueryGroupResponse]
    total: int
    page: int
    page_size: int


class RegroupRequest(BaseModel):
    """Schema for regrouping request."""

    codebase_id: int = Field(..., description="Codebase ID")
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Similarity threshold")
