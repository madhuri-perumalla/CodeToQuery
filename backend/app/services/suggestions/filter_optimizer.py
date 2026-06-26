"""Filter optimizer module for suggesting filter optimizations."""
import re
from dataclasses import dataclass
from typing import Any

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery

logger = get_logger(__name__)


@dataclass
class FilterOptimization:
    """Represents a filter optimization suggestion."""

    optimization_type: str  # sargable_expression, function_on_column, type_coercion, null_handling
    original_condition: str
    optimized_condition: str
    reason: str
    confidence_score: float
    impact_estimate: str  # high, medium, low
    related_query_id: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "optimization_type": self.optimization_type,
            "original_condition": self.original_condition,
            "optimized_condition": self.optimized_condition,
            "reason": self.reason,
            "confidence_score": self.confidence_score,
            "impact_estimate": self.impact_estimate,
            "related_query_id": self.related_query_id,
        }


class FilterOptimizer:
    """Optimizes filter conditions for better performance."""

    def __init__(self) -> None:
        """Initialize filter optimizer."""
        self.non_sargable_patterns = [
            r"(\w+)\s*=\s*UPPER\((\w+)\)",  # column = UPPER(column)
            r"(\w+)\s*=\s*LOWER\((\w+)\)",  # column = LOWER(column)
            r"(\w+)\s*=\s*TRIM\((\w+)\)",  # column = TRIM(column)
            r"(\w+)\s*=\s*SUBSTR\((\w+)",  # column = SUBSTR(column)
            r"(\w+)\s*=\s*CONCAT\((\w+)",  # column = CONCAT(column)
        ]

        self.function_on_column_patterns = [
            r"UPPER\((\w+)\)",  # UPPER(column)
            r"LOWER\((\w+)\)",  # LOWER(column)
            r"TRIM\((\w+)\)",  # TRIM(column)
            r"SUBSTR\((\w+)",  # SUBSTR(column)
            r"SUBSTRING\((\w+)",  # SUBSTRING(column)
            r"DATE\((\w+)\)",  # DATE(column)
            r"YEAR\((\w+)\)",  # YEAR(column)
            r"MONTH\((\w+)\)",  # MONTH(column)
            r"DAY\((\w+)\)",  # DAY(column)
        ]

    def analyze_query_for_filter_optimizations(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[FilterOptimization]:
        """
        Analyze a query for filter optimization opportunities.

        Args:
            query: Extracted query
            plan: Execution plan

        Returns:
            List of filter optimizations
        """
        optimizations = []

        # Detect non-sargable expressions
        sargable_optimizations = self._detect_non_sargable_expressions(query)
        optimizations.extend(sargable_optimizations)

        # Detect function calls on indexed columns
        function_optimizations = self._detect_functions_on_columns(query)
        optimizations.extend(function_optimizations)

        # Detect type coercion
        type_optimizations = self._detect_type_coercion(query)
        optimizations.extend(type_optimizations)

        # Detect NULL handling issues
        null_optimizations = self._detect_null_handling(query)
        optimizations.extend(null_optimizations)

        # Detect LIKE pattern optimization
        like_optimizations = self._detect_like_optimization(query)
        optimizations.extend(like_optimizations)

        return optimizations

    def _detect_non_sargable_expressions(self, query: ExtractedQuery) -> list[FilterOptimization]:
        """Detect non-sargable expressions in WHERE clause."""
        optimizations = []

        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return optimizations

        where_clause = where_match.group(1)

        for pattern in self.non_sargable_patterns:
            matches = re.finditer(pattern, where_clause, re.IGNORECASE)

            for match in matches:
                original_condition = match.group(0)

                optimization = FilterOptimization(
                    optimization_type="sargable_expression",
                    original_condition=original_condition,
                    optimized_condition=self._optimize_non_sargable(original_condition),
                    reason="Non-sargable expression prevents index usage - rewrite to be sargable",
                    confidence_score=0.85,
                    impact_estimate="high",
                    related_query_id=query.id,
                )
                optimizations.append(optimization)

        return optimizations

    def _optimize_non_sargable(self, condition: str) -> str:
        """Optimize non-sargable expression."""
        # Rewrite column = UPPER(column) to UPPER(column) = UPPER(column)
        # or better, use functional index
        return f"-- Consider using functional index or rewrite: {condition}"

    def _detect_functions_on_columns(self, query: ExtractedQuery) -> list[FilterOptimization]:
        """Detect function calls on columns in WHERE clause."""
        optimizations = []

        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return optimizations

        where_clause = where_match.group(1)

        for pattern in self.function_on_column_patterns:
            matches = re.finditer(pattern, where_clause, re.IGNORECASE)

            for match in matches:
                original_condition = match.group(0)
                column = match.group(1)

                optimization = FilterOptimization(
                    optimization_type="function_on_column",
                    original_condition=original_condition,
                    optimized_condition=f"-- Consider functional index on {column} or rewrite query",
                    reason=f"Function call on column '{column}' prevents index usage",
                    confidence_score=0.9,
                    impact_estimate="high",
                    related_query_id=query.id,
                )
                optimizations.append(optimization)

        return optimizations

    def _detect_type_coercion(self, query: ExtractedQuery) -> list[FilterOptimization]:
        """Detect implicit type conversions in WHERE clause."""
        optimizations = []

        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return optimizations

        where_clause = where_match.group(1)

        # Detect patterns like: numeric_column = 'string' or string_column = 123
        type_patterns = [
            r"(\w+)\s*=\s*['\"]\d+['\"]",  # column = '123'
            r"(\w+)\s*=\s*\d+",  # column = 123 (if column is string)
        ]

        for pattern in type_patterns:
            matches = re.finditer(pattern, where_clause, re.IGNORECASE)

            for match in matches:
                original_condition = match.group(0)
                column = match.group(1)

                optimization = FilterOptimization(
                    optimization_type="type_coercion",
                    original_condition=original_condition,
                    optimized_condition=f"-- Ensure matching types: {column} = value",
                    reason=f"Implicit type conversion on '{column}' may prevent index usage",
                    confidence_score=0.75,
                    impact_estimate="medium",
                    related_query_id=query.id,
                )
                optimizations.append(optimization)

        return optimizations

    def _detect_null_handling(self, query: ExtractedQuery) -> list[FilterOptimization]:
        """Detect NULL handling issues in WHERE clause."""
        optimizations = []

        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return optimizations

        where_clause = where_match.group(1)

        # Detect patterns like: column IS NULL or column IS NOT NULL
        null_patterns = [
            r"(\w+)\s+IS\s+NULL",
            r"(\w+)\s+IS\s+NOT\s+NULL",
        ]

        for pattern in null_patterns:
            matches = re.finditer(pattern, where_clause, re.IGNORECASE)

            for match in matches:
                original_condition = match.group(0)
                column = match.group(1)

                optimization = FilterOptimization(
                    optimization_type="null_handling",
                    original_condition=original_condition,
                    optimized_condition=f"-- Consider using COALESCE or partial index for {column}",
                    reason=f"NULL comparison on '{column}' may not use index efficiently",
                    confidence_score=0.6,
                    impact_estimate="medium",
                    related_query_id=query.id,
                )
                optimizations.append(optimization)

        return optimizations

    def _detect_like_optimization(self, query: ExtractedQuery) -> list[FilterOptimization]:
        """Detect LIKE pattern optimization opportunities."""
        optimizations = []

        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return optimizations

        where_clause = where_match.group(1)

        # Detect LIKE with leading wildcard
        like_pattern = r"(\w+)\s+LIKE\s+['\"]%[^%]"

        matches = re.finditer(like_pattern, where_clause, re.IGNORECASE)

        for match in matches:
            original_condition = match.group(0)
            column = match.group(1)

            optimization = FilterOptimization(
                optimization_type="like_optimization",
                original_condition=original_condition,
                optimized_condition=f"-- Consider using full-text search or trigram index for {column}",
                reason=f"LIKE with leading wildcard on '{column}' prevents index usage",
                confidence_score=0.9,
                impact_estimate="high",
                related_query_id=query.id,
            )
            optimizations.append(optimization)

        return optimizations

    def suggest_index_for_function(self, column: str, function: str, query_id: int) -> FilterOptimization:
        """
        Suggest functional index for function on column.

        Args:
            column: Column name
            function: Function name
            query_id: Query ID

        Returns:
            Filter optimization
        """
        return FilterOptimization(
            optimization_type="function_on_column",
            original_condition=f"{function}({column})",
            optimized_condition=f"CREATE INDEX idx_{column}_{function.lower()} ON table ({function}({column}));",
            reason=f"Create functional index for {function}({column})",
            confidence_score=0.85,
            impact_estimate="high",
            related_query_id=query_id,
        )

    def suggest_partial_index_for_null(self, column: str, query_id: int) -> FilterOptimization:
        """
        Suggest partial index for NULL handling.

        Args:
            column: Column name
            query_id: Query ID

        Returns:
            Filter optimization
        """
        return FilterOptimization(
            optimization_type="null_handling",
            original_condition=f"{column} IS NOT NULL",
            optimized_condition=f"CREATE INDEX idx_{column}_not_null ON table ({column}) WHERE {column} IS NOT NULL;",
            reason=f"Create partial index for {column} IS NOT NULL",
            confidence_score=0.75,
            impact_estimate="medium",
            related_query_id=query_id,
        )

    def suggest_trigram_index(self, column: str, query_id: int) -> FilterOptimization:
        """
        Suggest trigram index for LIKE patterns.

        Args:
            column: Column name
            query_id: Query ID

        Returns:
            Filter optimization
        """
        return FilterOptimization(
            optimization_type="like_optimization",
            original_condition=f"{column} LIKE '%pattern%'",
            optimized_condition=f"CREATE INDEX idx_{column}_trigram ON table USING GIN ({column} gin_trgm_ops);",
            reason=f"Create trigram index for LIKE patterns on {column}",
            confidence_score=0.85,
            impact_estimate="high",
            related_query_id=query_id,
        )
