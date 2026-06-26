"""Main suggestion service for coordinating all suggestion modules."""
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.diagnostic import Diagnostic
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery
from app.models.suggestion import FixSuggestion
from app.services.suggestions.filter_optimizer import FilterOptimization, FilterOptimizer
from app.services.suggestions.index_recommender import IndexRecommendation, IndexRecommender
from app.services.suggestions.query_rewrite_advisor import QueryRewriteAdvisor, RewriteSuggestion

logger = get_logger(__name__)


class SuggestionService:
    """Main service for generating fix suggestions."""

    def __init__(self) -> None:
        """Initialize suggestion service."""
        self.index_recommender = IndexRecommender()
        self.query_rewrite_advisor = QueryRewriteAdvisor()
        self.filter_optimizer = FilterOptimizer()

    def generate_suggestions_for_query(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
        db: Session,
    ) -> dict[str, Any]:
        """
        Generate all suggestions for a query.

        Args:
            query: Extracted query
            plan: Execution plan
            db: Database session

        Returns:
            Dictionary with all suggestions
        """
        suggestions = {
            "index_recommendations": [],
            "rewrite_suggestions": [],
            "filter_optimizations": [],
        }

        # Generate index recommendations
        index_recommendations = self.index_recommender.analyze_query_for_indexes(query, plan)
        suggestions["index_recommendations"] = [rec.to_dict() for rec in index_recommendations]

        # Generate rewrite suggestions
        rewrite_suggestions = self.query_rewrite_advisor.analyze_query_for_rewrites(query, plan)
        suggestions["rewrite_suggestions"] = [sug.to_dict() for sug in rewrite_suggestions]

        # Generate filter optimizations
        filter_optimizations = self.filter_optimizer.analyze_query_for_filter_optimizations(query, plan)
        suggestions["filter_optimizations"] = [opt.to_dict() for opt in filter_optimizations]

        return suggestions

    def generate_suggestions_for_diagnostic(
        self,
        diagnostic: Diagnostic,
        db: Session,
    ) -> list[dict[str, Any]]:
        """
        Generate suggestions for a diagnostic.

        Args:
            diagnostic: Diagnostic object
            db: Database session

        Returns:
            List of suggestions
        """
        suggestions = []

        # Get the query and plan
        query = db.query(ExtractedQuery).filter(ExtractedQuery.id == diagnostic.query_id).first()
        if not query:
            return suggestions

        plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query.id).first()

        # Generate suggestions based on diagnostic type
        if diagnostic.rule_id == "sequential_scan":
            suggestions.extend(self._generate_sequential_scan_suggestions(query, plan))
        elif diagnostic.rule_id == "high_cost":
            suggestions.extend(self._generate_high_cost_suggestions(query, plan))
        elif diagnostic.rule_id == "missing_index":
            suggestions.extend(self._generate_missing_index_suggestions(query, plan))
        elif diagnostic.rule_id == "expensive_join":
            suggestions.extend(self._generate_expensive_join_suggestions(query, plan))
        elif diagnostic.rule_id == "large_row_estimation":
            suggestions.extend(self._generate_row_estimation_suggestions(query, plan))

        return suggestions

    def _generate_sequential_scan_suggestions(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[dict[str, Any]]:
        """Generate suggestions for sequential scan diagnostic."""
        suggestions = []

        # Get index recommendations
        index_recommendations = self.index_recommender.analyze_query_for_indexes(query, plan)

        for rec in index_recommendations:
            suggestion = {
                "suggestion_type": "add_index",
                "description": f"Add index on {rec.table_name}.{', '.join(rec.column_names)}",
                "sql_change": rec.sql_statement,
                "impact_estimate": rec.impact_estimate,
                "confidence_score": rec.confidence_score,
                "metadata": {
                    "table_name": rec.table_name,
                    "column_names": rec.column_names,
                    "index_type": rec.index_type,
                    "reason": rec.reason,
                },
            }
            suggestions.append(suggestion)

        return suggestions

    def _generate_high_cost_suggestions(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[dict[str, Any]]:
        """Generate suggestions for high cost diagnostic."""
        suggestions = []

        # Get rewrite suggestions
        rewrite_suggestions = self.query_rewrite_advisor.analyze_query_for_rewrites(query, plan)

        for sug in rewrite_suggestions:
            suggestion = {
                "suggestion_type": "rewrite_query",
                "description": sug.reason,
                "sql_change": sug.rewritten_sql,
                "impact_estimate": sug.impact_estimate,
                "confidence_score": sug.confidence_score,
                "metadata": {
                    "original_sql": sug.original_sql,
                    "suggestion_type": sug.suggestion_type,
                },
            }
            suggestions.append(suggestion)

        # Suggest materialized view for very expensive queries
        if plan and plan.total_cost and plan.total_cost > 5000:
            materialized_suggestions = self.query_rewrite_advisor.suggest_materialized_view(query, plan)
            for sug in materialized_suggestions:
                suggestion = {
                    "suggestion_type": "add_materialized_view",
                    "description": sug.reason,
                    "sql_change": sug.rewritten_sql,
                    "impact_estimate": sug.impact_estimate,
                    "confidence_score": sug.confidence_score,
                    "metadata": {
                        "original_sql": sug.original_sql,
                    },
                }
                suggestions.append(suggestion)

        return suggestions

    def _generate_missing_index_suggestions(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[dict[str, Any]]:
        """Generate suggestions for missing index diagnostic."""
        suggestions = []

        # Get index recommendations
        index_recommendations = self.index_recommender.analyze_query_for_indexes(query, plan)

        for rec in index_recommendations:
            suggestion = {
                "suggestion_type": "add_index",
                "description": f"Add {rec.index_type} index on {rec.table_name}.{', '.join(rec.column_names)}",
                "sql_change": rec.sql_statement,
                "impact_estimate": rec.impact_estimate,
                "confidence_score": rec.confidence_score,
                "metadata": {
                    "table_name": rec.table_name,
                    "column_names": rec.column_names,
                    "index_type": rec.index_type,
                    "recommendation_type": rec.recommendation_type,
                    "reason": rec.reason,
                },
            }
            suggestions.append(suggestion)

        return suggestions

    def _generate_expensive_join_suggestions(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[dict[str, Any]]:
        """Generate suggestions for expensive join diagnostic."""
        suggestions = []

        # Get index recommendations for join columns
        index_recommendations = self.index_recommender.analyze_query_for_indexes(query, plan)

        for rec in index_recommendations:
            if rec.reason and "JOIN" in rec.reason.upper():
                suggestion = {
                    "suggestion_type": "add_index",
                    "description": f"Add index on join column {rec.table_name}.{', '.join(rec.column_names)}",
                    "sql_change": rec.sql_statement,
                    "impact_estimate": rec.impact_estimate,
                    "confidence_score": rec.confidence_score,
                    "metadata": {
                        "table_name": rec.table_name,
                        "column_names": rec.column_names,
                        "index_type": rec.index_type,
                        "reason": rec.reason,
                    },
                }
                suggestions.append(suggestion)

        # Suggest join order optimization
        join_order_suggestions = self.query_rewrite_advisor.suggest_join_order(query, plan)
        for sug in join_order_suggestions:
            suggestion = {
                "suggestion_type": "change_join_order",
                "description": sug.reason,
                "sql_change": sug.rewritten_sql,
                "impact_estimate": sug.impact_estimate,
                "confidence_score": sug.confidence_score,
                "metadata": {
                    "original_sql": sug.original_sql,
                },
            }
            suggestions.append(suggestion)

        return suggestions

    def _generate_row_estimation_suggestions(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[dict[str, Any]]:
        """Generate suggestions for large row estimation diagnostic."""
        suggestions = []

        # Suggest ANALYZE to update statistics
        suggestion = {
            "suggestion_type": "analyze_table",
            "description": "Run ANALYZE on affected tables to update statistics",
            "sql_change": "-- Run ANALYZE on tables used in query\nANALYZE table_name;",
            "impact_estimate": "medium",
            "confidence_score": 0.8,
            "metadata": {
                "reason": "Row estimation mismatch suggests outdated statistics",
            },
        }
        suggestions.append(suggestion)

        # Get filter optimizations
        filter_optimizations = self.filter_optimizer.analyze_query_for_filter_optimizations(query, plan)

        for opt in filter_optimizations:
            suggestion = {
                "suggestion_type": "optimize_filter",
                "description": opt.reason,
                "sql_change": opt.optimized_condition,
                "impact_estimate": opt.impact_estimate,
                "confidence_score": opt.confidence_score,
                "metadata": {
                    "original_condition": opt.original_condition,
                    "optimization_type": opt.optimization_type,
                },
            }
            suggestions.append(suggestion)

        return suggestions

    def save_suggestions_to_db(
        self,
        diagnostic_id: int,
        suggestions: list[dict[str, Any]],
        db: Session,
    ) -> list[FixSuggestion]:
        """
        Save suggestions to database.

        Args:
            diagnostic_id: Diagnostic ID
            suggestions: List of suggestion dictionaries
            db: Database session

        Returns:
            List of created FixSuggestion objects
        """
        created_suggestions = []

        for suggestion_data in suggestions:
            fix_suggestion = FixSuggestion(
                diagnostic_id=diagnostic_id,
                suggestion_type=suggestion_data.get("suggestion_type", "rewrite_query"),
                description=suggestion_data.get("description", ""),
                sql_change=suggestion_data.get("sql_change"),
                impact_estimate=suggestion_data.get("impact_estimate", "medium"),
                confidence_score=suggestion_data.get("confidence_score", 0.5),
                metadata=suggestion_data.get("metadata", {}),
            )

            db.add(fix_suggestion)
            created_suggestions.append(fix_suggestion)

        db.commit()

        for suggestion in created_suggestions:
            db.refresh(suggestion)

        return created_suggestions

    def get_suggestions_for_diagnostic(
        self,
        diagnostic_id: int,
        db: Session,
    ) -> list[dict[str, Any]]:
        """
        Get suggestions for a diagnostic.

        Args:
            diagnostic_id: Diagnostic ID
            db: Database session

        Returns:
            List of suggestion dictionaries
        """
        suggestions = db.query(FixSuggestion).filter(FixSuggestion.diagnostic_id == diagnostic_id).all()

        return [suggestion.to_dict() for suggestion in suggestions]

    def get_all_suggestions_for_codebase(
        self,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Get all suggestions for a codebase.

        Args:
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Dictionary with all suggestions grouped by type
        """
        from app.models.query import ExtractedQuery

        # Get all queries in codebase
        queries = db.query(ExtractedQuery).filter(ExtractedQuery.codebase_id == codebase_id).all()

        all_suggestions = {
            "add_index": [],
            "rewrite_query": [],
            "optimize_filter": [],
            "analyze_table": [],
            "change_join_order": [],
            "add_materialized_view": [],
        }

        total_suggestions = 0
        high_impact_count = 0

        for query in queries:
            plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query.id).first()

            # Get all diagnostics for this query
            diagnostics = db.query(Diagnostic).filter(Diagnostic.query_id == query.id).all()

            for diagnostic in diagnostics:
                suggestions = self.get_suggestions_for_diagnostic(diagnostic.id, db)

                for suggestion in suggestions:
                    suggestion_type = suggestion.get("suggestion_type", "rewrite_query")
                    if suggestion_type in all_suggestions:
                        all_suggestions[suggestion_type].append(suggestion)

                    total_suggestions += 1

                    if suggestion.get("impact_estimate") == "high":
                        high_impact_count += 1

        return {
            "codebase_id": codebase_id,
            "total_suggestions": total_suggestions,
            "high_impact_count": high_impact_count,
            "suggestions_by_type": all_suggestions,
        }

    def apply_suggestion(
        self,
        suggestion_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Apply a suggestion (mark as applied).

        Args:
            suggestion_id: Suggestion ID
            db: Database session

        Returns:
            Updated suggestion
        """
        suggestion = db.query(FixSuggestion).filter(FixSuggestion.id == suggestion_id).first()

        if not suggestion:
            return {"error": "Suggestion not found"}

        # Mark as applied
        suggestion.meta_data["applied"] = True
        suggestion.meta_data["applied_at"] = str(datetime.utcnow())

        db.commit()
        db.refresh(suggestion)

        return suggestion.to_dict()
