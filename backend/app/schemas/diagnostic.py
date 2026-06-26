"""Diagnostic schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DiagnosticResponse(BaseModel):
    """Schema for diagnostic response."""

    id: int
    plan_id: int
    rule_id: str
    severity: str
    message: str
    location: dict[str, Any] | None
    metadata: dict[str, Any]
    created_at: datetime
    suggestions: list[dict[str, Any]] = []

    class Config:
        """Pydantic config."""

        from_attributes = True


class DiagnosticListResponse(BaseModel):
    """Schema for diagnostic list response."""

    items: list[DiagnosticResponse]
    total: int
    page: int
    page_size: int


class DiagnosticSummary(BaseModel):
    """Schema for diagnostic summary."""

    codebase_id: int
    total_diagnostics: int
    by_severity: dict[str, int]
    by_rule: dict[str, int]
    top_rules: list[dict[str, Any]]
