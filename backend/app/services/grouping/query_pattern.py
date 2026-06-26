"""Query pattern data structures."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryPattern:
    """Represents a query pattern identified from normalized AST structures."""

    pattern_id: str
    pattern_type: str  # duplicate, expensive, anti_pattern, common
    pattern_signature: str  # Normalized AST signature
    query_count: int
    files_impacted: list[str]
    total_cost: float
    max_cost: float
    avg_cost: float
    total_rows: int
    max_rows: int
    avg_rows: int
    risk_score: float
    severity: str  # critical, high, medium, low
    sample_query_id: int | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "pattern_signature": self.pattern_signature,
            "query_count": self.query_count,
            "files_impacted": self.files_impacted,
            "total_cost": self.total_cost,
            "max_cost": self.max_cost,
            "avg_cost": self.avg_cost,
            "total_rows": self.total_rows,
            "max_rows": self.max_rows,
            "avg_rows": self.avg_rows,
            "risk_score": self.risk_score,
            "severity": self.severity,
            "sample_query_id": self.sample_query_id,
            "metadata": self.meta_data,
        }


@dataclass
class PatternMatch:
    """Represents a query matching a pattern."""

    query_id: int
    pattern_id: str
    similarity_score: float
    cost: float
    rows: int
    file_path: str
    line_number: int
    function_name: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "pattern_id": self.pattern_id,
            "similarity_score": self.similarity_score,
            "cost": self.cost,
            "rows": self.rows,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "function_name": self.function_name,
        }


@dataclass
class PatternStatistics:
    """Statistics for query patterns."""

    total_patterns: int
    duplicate_patterns: int
    expensive_patterns: int
    anti_patterns: int
    common_patterns: int
    total_queries_analyzed: int
    queries_in_patterns: int
    unique_queries: int
    avg_queries_per_pattern: float
    high_risk_patterns: int
    medium_risk_patterns: int
    low_risk_patterns: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_patterns": self.total_patterns,
            "duplicate_patterns": self.duplicate_patterns,
            "expensive_patterns": self.expensive_patterns,
            "anti_patterns": self.anti_patterns,
            "common_patterns": self.common_patterns,
            "total_queries_analyzed": self.total_queries_analyzed,
            "queries_in_patterns": self.queries_in_patterns,
            "unique_queries": self.unique_queries,
            "avg_queries_per_pattern": self.avg_queries_per_pattern,
            "high_risk_patterns": self.high_risk_patterns,
            "medium_risk_patterns": self.medium_risk_patterns,
            "low_risk_patterns": self.low_risk_patterns,
        }
