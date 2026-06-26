"""Suggestion schemas for API requests and responses."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IndexRecommendationSchema(BaseModel):
    """Schema for index recommendation."""

    table_name: str = Field(..., description="Table name")
    column_names: list[str] = Field(..., description="Column names for index")
    index_type: str = Field(..., description="Index type (btree, hash, gin, gist)")
    recommendation_type: str = Field(..., description="Recommendation type (single_column, composite, partial)")
    selectivity_estimate: float = Field(..., description="Estimated selectivity")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    impact_estimate: str = Field(..., description="Impact estimate (high, medium, low)")
    reason: str = Field(..., description="Reason for recommendation")
    sql_statement: str = Field(..., description="SQL statement to create index")
    related_query_ids: list[int] = Field(default_factory=list, description="Related query IDs")

    model_config = {"from_attributes": True}


class RewriteSuggestionSchema(BaseModel):
    """Schema for query rewrite suggestion."""

    suggestion_type: str = Field(..., description="Suggestion type")
    original_sql: str = Field(..., description="Original SQL")
    rewritten_sql: str = Field(..., description="Rewritten SQL")
    reason: str = Field(..., description="Reason for suggestion")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    impact_estimate: str = Field(..., description="Impact estimate (high, medium, low)")
    related_query_id: int = Field(..., description="Related query ID")

    model_config = {"from_attributes": True}


class FilterOptimizationSchema(BaseModel):
    """Schema for filter optimization."""

    optimization_type: str = Field(..., description="Optimization type")
    original_condition: str = Field(..., description="Original condition")
    optimized_condition: str = Field(..., description="Optimized condition")
    reason: str = Field(..., description="Reason for optimization")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    impact_estimate: str = Field(..., description="Impact estimate (high, medium, low)")
    related_query_id: int = Field(..., description="Related query ID")

    model_config = {"from_attributes": True}


class FixSuggestionCreate(BaseModel):
    """Schema for creating a fix suggestion."""

    diagnostic_id: int = Field(..., description="Diagnostic ID")
    suggestion_type: str = Field(..., description="Suggestion type")
    description: str = Field(..., description="Description")
    sql_change: str | None = Field(None, description="SQL change")
    impact_estimate: str = Field(..., description="Impact estimate")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FixSuggestionUpdate(BaseModel):
    """Schema for updating a fix suggestion."""

    description: str | None = Field(None, description="Description")
    sql_change: str | None = Field(None, description="SQL change")
    impact_estimate: str | None = Field(None, description="Impact estimate")
    confidence_score: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FixSuggestionResponse(BaseModel):
    """Schema for fix suggestion response."""

    id: int
    diagnostic_id: int
    suggestion_type: str
    description: str
    sql_change: str | None
    impact_estimate: str
    confidence_score: float | None
    metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class QuerySuggestionsResponse(BaseModel):
    """Schema for query suggestions response."""

    query_id: int
    index_recommendations: list[IndexRecommendationSchema]
    rewrite_suggestions: list[RewriteSuggestionSchema]
    filter_optimizations: list[FilterOptimizationSchema]

    model_config = {"from_attributes": True}


class CodebaseSuggestionsResponse(BaseModel):
    """Schema for codebase suggestions response."""

    codebase_id: int
    total_suggestions: int
    high_impact_count: int
    suggestions_by_type: dict[str, list[dict[str, Any]]]

    model_config = {"from_attributes": True}


class ApplySuggestionRequest(BaseModel):
    """Schema for applying a suggestion."""

    suggestion_id: int = Field(..., description="Suggestion ID")


class ApplySuggestionResponse(BaseModel):
    """Schema for apply suggestion response."""

    success: bool
    message: str
    suggestion: FixSuggestionResponse | None = None
