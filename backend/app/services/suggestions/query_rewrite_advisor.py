"""Query rewrite advisor module for suggesting query optimizations."""
import re
from dataclasses import dataclass
from typing import Any

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery

logger = get_logger(__name__)


@dataclass
class RewriteSuggestion:
    """Represents a query rewrite suggestion."""

    suggestion_type: str  # subquery_to_join, add_cte, filter_pushdown, add_limit, etc.
    original_sql: str
    rewritten_sql: str
    reason: str
    confidence_score: float
    impact_estimate: str  # high, medium, low
    related_query_id: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suggestion_type": self.suggestion_type,
            "original_sql": self.original_sql,
            "rewritten_sql": self.rewritten_sql,
            "reason": self.reason,
            "confidence_score": self.confidence_score,
            "impact_estimate": self.impact_estimate,
            "related_query_id": self.related_query_id,
        }


class QueryRewriteAdvisor:
    """Advises on query rewrites for optimization."""

    def __init__(self) -> None:
        """Initialize query rewrite advisor."""
        pass

    def analyze_query_for_rewrites(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[RewriteSuggestion]:
        """
        Analyze a query for rewrite opportunities.

        Args:
            query: Extracted query
            plan: Execution plan

        Returns:
            List of rewrite suggestions
        """
        suggestions = []

        # Check for subqueries in SELECT clause
        subquery_suggestions = self._detect_subquery_in_select(query)
        suggestions.extend(subquery_suggestions)

        # Check for opportunities to add CTE
        cte_suggestions = self._suggest_cte(query)
        suggestions.extend(cte_suggestions)

        # Check for filter pushdown opportunities
        filter_suggestions = self._suggest_filter_pushdown(query, plan)
        suggestions.extend(filter_suggestions)

        # Check for missing LIMIT
        limit_suggestions = self._suggest_limit(query)
        suggestions.extend(limit_suggestions)

        # Check for DISTINCT optimization
        distinct_suggestions = self._suggest_distinct_optimization(query)
        suggestions.extend(distinct_suggestions)

        # Check for UNION vs OR
        union_suggestions = self._suggest_union(query)
        suggestions.extend(union_suggestions)

        return suggestions

    def _detect_subquery_in_select(self, query: ExtractedQuery) -> list[RewriteSuggestion]:
        """Detect subqueries in SELECT clause that could be converted to JOINs."""
        suggestions = []

        # Pattern: SELECT ..., (SELECT ...) FROM ...
        pattern = r"SELECT\s+.*?\(\s*SELECT\s+.*?\)\s+.*?FROM"

        if re.search(pattern, query.normalized_sql, re.IGNORECASE | re.DOTALL):
            suggestion = RewriteSuggestion(
                suggestion_type="subquery_to_join",
                original_sql=query.normalized_sql,
                rewritten_sql=self._rewrite_subquery_to_join(query.normalized_sql),
                reason="Subquery in SELECT clause executed for each row - consider using JOIN",
                confidence_score=0.85,
                impact_estimate="high",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _rewrite_subquery_to_join(self, sql: str) -> str:
        """Rewrite subquery to JOIN (simplified)."""
        # This is a simplified version - real implementation would need proper SQL parsing
        return "-- Rewrite subquery to LEFT JOIN for better performance\n" + sql

    def _suggest_cte(self, query: ExtractedQuery) -> list[RewriteSuggestion]:
        """Suggest using Common Table Expressions for complex queries."""
        suggestions = []

        # Check for repeated subqueries or complex nested queries
        nested_count = sql.lower().count("select")

        if nested_count >= 3:
            suggestion = RewriteSuggestion(
                suggestion_type="add_cte",
                original_sql=query.normalized_sql,
                rewritten_sql=self._add_cte(query.normalized_sql),
                reason="Complex nested query - consider using CTE for readability and potential optimization",
                confidence_score=0.7,
                impact_estimate="medium",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _add_cte(self, sql: str) -> str:
        """Add CTE to query (simplified)."""
        return "-- Add WITH clause (CTE) for better structure\nWITH cte_name AS (\n  -- Extract repeated subquery here\n)\n" + sql

    def _suggest_filter_pushdown(self, query: ExtractedQuery, plan: ExecutionPlanModel | None) -> list[RewriteSuggestion]:
        """Suggest pushing filters earlier in the query execution."""
        suggestions = []

        if not plan:
            return suggestions

        # Check for late filtering in execution plan
        def check_late_filter(node: dict[str, Any], depth: int = 0) -> bool:
            """Check if filter is applied late in the plan."""
            node_type = node.get("Node Type", "")

            if node_type == "Filter" and depth > 2:
                return True

            if "Plans" in node:
                for child in node["Plans"]:
                    if check_late_filter(child, depth + 1):
                        return True

            return False

        if check_late_filter(plan.plan_json):
            suggestion = RewriteSuggestion(
                suggestion_type="filter_pushdown",
                original_sql=query.normalized_sql,
                rewritten_sql=self._push_down_filters(query.normalized_sql),
                reason="Filter applied late in execution plan - consider pushing filters earlier",
                confidence_score=0.75,
                impact_estimate="high",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _push_down_filters(self, sql: str) -> str:
        """Push down filters in query (simplified)."""
        return "-- Move WHERE conditions to subqueries for early filtering\n" + sql

    def _suggest_limit(self, query: ExtractedQuery) -> list[RewriteSuggestion]:
        """Suggest adding LIMIT clause for queries without it."""
        suggestions = []

        # Check if query has LIMIT
        has_limit = re.search(r"\bLIMIT\b", query.normalized_sql, re.IGNORECASE)

        # Check if it's a SELECT query
        is_select = re.search(r"\bSELECT\b", query.normalized_sql, re.IGNORECASE)

        # Check if it's not an aggregate query (COUNT, SUM, etc.)
        is_aggregate = re.search(r"\b(COUNT|SUM|AVG|MAX|MIN)\s*\(", query.normalized_sql, re.IGNORECASE)

        if is_select and not has_limit and not is_aggregate:
            suggestion = RewriteSuggestion(
                suggestion_type="add_limit",
                original_sql=query.normalized_sql,
                rewritten_sql=query.normalized_sql + " LIMIT 1000;",
                reason="Query without LIMIT may return large result sets - consider adding LIMIT for safety",
                confidence_score=0.6,
                impact_estimate="medium",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _suggest_distinct_optimization(self, query: ExtractedQuery) -> list[RewriteSuggestion]:
        """Suggest optimizations for DISTINCT queries."""
        suggestions = []

        # Check for DISTINCT
        has_distinct = re.search(r"\bDISTINCT\b", query.normalized_sql, re.IGNORECASE)

        if has_distinct:
            # Check if DISTINCT can be replaced with GROUP BY
            suggestion = RewriteSuggestion(
                suggestion_type="distinct_to_group_by",
                original_sql=query.normalized_sql,
                rewritten_sql=self._rewrite_distinct_to_group_by(query.normalized_sql),
                reason="DISTINCT can sometimes be optimized using GROUP BY with indexes",
                confidence_score=0.65,
                impact_estimate="medium",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions

    def _rewrite_distinct_to_group_by(self, sql: str) -> str:
        """Rewrite DISTINCT to GROUP BY (simplified)."""
        return "-- Consider using GROUP BY instead of DISTINCT for better index usage\n" + sql

    def _suggest_union(self, query: ExtractedQuery) -> list[RewriteSuggestion]:
        """Suggest using UNION instead of OR for better index usage."""
        suggestions = []

        # Check for OR conditions in WHERE clause
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)", query.normalized_sql, re.IGNORECASE)

        if where_match:
            where_clause = where_match.group(1)

            # Count OR conditions
            or_count = len(re.findall(r"\bOR\b", where_clause, re.IGNORECASE))

            if or_count >= 2:
                suggestion = RewriteSuggestion(
                    suggestion_type="or_to_union",
                    original_sql=query.normalized_sql,
                    rewritten_sql=self._rewrite_or_to_union(query.normalized_sql),
                    reason="Multiple OR conditions may prevent index usage - consider using UNION",
                    confidence_score=0.7,
                    impact_estimate="high",
                    related_query_id=query.id,
                )
                suggestions.append(suggestion)

        return suggestions

    def _rewrite_or_to_union(self, sql: str) -> str:
        """Rewrite OR to UNION (simplified)."""
        return "-- Consider splitting OR conditions into UNION queries for better index usage\n" + sql

    def suggest_join_order(self, query: ExtractedQuery, plan: ExecutionPlanModel | None) -> list[RewriteSuggestion]:
        """Suggest optimal join order based on execution plan."""
        suggestions = []

        if not plan:
            return suggestions

        # Analyze join order in execution plan
        def analyze_join_order(node: dict[str, Any], path: list[str] = []) -> None:
            """Analyze join order."""
            node_type = node.get("Node Type", "")

            if "Join" in node_type:
                # Check join order
                if "Plans" in node and len(node["Plans"]) >= 2:
                    # This is simplified - real implementation would analyze cardinality
                    suggestion = RewriteSuggestion(
                        suggestion_type="join_order",
                        original_sql=query.normalized_sql,
                        rewritten_sql="-- Consider reordering joins based on table sizes\n" + query.normalized_sql,
                        reason="Join order may not be optimal - consider joining smaller tables first",
                        confidence_score=0.6,
                        impact_estimate="medium",
                        related_query_id=query.id,
                    )
                    suggestions.append(suggestion)

            if "Plans" in node:
                for child in node["Plans"]:
                    analyze_join_order(child, path + [node_type])

        analyze_join_order(plan.plan_json)

        return suggestions

    def suggest_materialized_view(self, query: ExtractedQuery, plan: ExecutionPlanModel | None) -> list[RewriteSuggestion]:
        """Suggest using materialized views for expensive repeated queries."""
        suggestions = []

        if not plan:
            return suggestions

        # Check if query is expensive and likely to be repeated
        if plan.total_cost and plan.total_cost > 1000:
            suggestion = RewriteSuggestion(
                suggestion_type="materialized_view",
                original_sql=query.normalized_sql,
                rewritten_sql=f"-- Create materialized view:\nCREATE MATERIALIZED VIEW mv_query_{query.id} AS\n{query.normalized_sql};",
                reason="Expensive query that could benefit from materialized view for repeated execution",
                confidence_score=0.5,
                impact_estimate="high",
                related_query_id=query.id,
            )
            suggestions.append(suggestion)

        return suggestions
