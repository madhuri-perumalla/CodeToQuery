"""EXPLAIN analysis service."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import AnalysisError, ExternalServiceError
from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan
from app.models.query import ExtractedQuery
from app.services.explain.explain_runner import ExplainRunner
from app.services.explain.metric_extractor import MetricExtractor
from app.services.explain.plan_parser import PlanParser

logger = get_logger(__name__)


class ExplainService:
    """Service for EXPLAIN analysis of SQL queries."""

    def __init__(self) -> None:
        """Initialize EXPLAIN service."""
        self.runner = ExplainRunner()
        self.parser = PlanParser()
        self.extractor = MetricExtractor()

    def analyze_query(
        self,
        query_id: int,
        db: Session,
        analyze: bool = False,
        timeout: int = 30,
    ) -> ExecutionPlan:
        """
        Analyze a query with EXPLAIN.

        Args:
            query_id: Query ID
            db: Database session
            analyze: Whether to use ANALYZE
            timeout: Query timeout

        Returns:
            Execution plan object

        Raises:
            AnalysisError: If analysis fails
        """
        # Get query
        query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
        if not query:
            raise AnalysisError("Query not found", query_id=query_id)

        try:
            logger.info(f"Analyzing query {query_id} with EXPLAIN")

            # Run EXPLAIN
            plan_json = self.runner.run_explain(
                query.normalized_sql,
                analyze=analyze,
                format="json",
                timeout=timeout,
            )

            # Parse plan
            parsed_plan = self.parser.parse_plan(plan_json)

            # Extract metrics
            metrics = self.extractor.extract_metrics(plan_json)

            # Generate plan hash
            plan_hash = self.parser.generate_plan_hash(parsed_plan)

            # Calculate total cost and rows
            total_cost = self.extractor.extract_nested_metrics(plan_json).get("total_cost", 0.0)
            total_rows = self.extractor.detect_expensive_nodes(plan_json)

            # Create execution plan record
            execution_plan = ExecutionPlan(
                query_id=query_id,
                plan_json=plan_json,
                plan_hash=plan_hash,
                total_cost=total_cost,
                total_rows=metrics.get("plan_rows", 0),
                plan_width=metrics.get("plan_width", 0),
                format="json",
                execution_time_ms=metrics.get("actual_total_time"),
                metadata={
                    "node_count": metrics.get("node_count"),
                    "plan_depth": metrics.get("plan_depth"),
                    "scan_types": metrics.get("scan_types"),
                    "scan_type": metrics.get("scan_type"),
                    "join_strategy": metrics.get("join_strategy"),
                    "relation_names": metrics.get("relation_names"),
                    "startup_cost": metrics.get("startup_cost"),
                    "analyzed": analyze,
                },
            )

            db.add(execution_plan)
            db.commit()
            db.refresh(execution_plan)

            logger.info(f"EXPLAIN analysis completed for query {query_id}")
            return execution_plan

        except ExternalServiceError as e:
            logger.error(f"EXPLAIN analysis failed for query {query_id}: {e}")
            raise AnalysisError("EXPLAIN execution failed", query_id=query_id, details=str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error during EXPLAIN analysis for query {query_id}: {e}")
            raise AnalysisError("EXPLAIN analysis failed", query_id=query_id, details=str(e)) from e

    def analyze_batch(
        self,
        query_ids: list[int],
        db: Session,
        analyze: bool = False,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze multiple queries with EXPLAIN.

        Args:
            query_ids: List of query IDs
            db: Database session
            analyze: Whether to use ANALYZE
            timeout: Query timeout

        Returns:
            Dictionary with analysis results
        """
        results = {
            "total": len(query_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for query_id in query_ids:
            try:
                self.analyze_query(query_id, db, analyze=analyze, timeout=timeout)
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "query_id": query_id,
                    "error": str(e),
                })
                logger.error(f"Failed to analyze query {query_id}: {e}")

        return results

    def get_plan_summary(self, plan_id: int, db: Session) -> dict[str, Any]:
        """
        Get summary of an execution plan.

        Args:
            plan_id: Execution plan ID
            db: Database session

        Returns:
            Plan summary dictionary

        Raises:
            AnalysisError: If plan not found
        """
        plan = db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise AnalysisError("Execution plan not found", plan_id=plan_id)

        # Extract metrics
        metrics = self.extractor.extract_metrics(plan.plan_json)

        return {
            "plan_id": plan_id,
            "query_id": plan.query_id,
            "total_cost": plan.total_cost,
            "total_rows": plan.total_rows,
            "plan_width": plan.plan_width,
            "execution_time_ms": plan.execution_time_ms,
            "node_count": metrics.get("node_count"),
            "plan_depth": metrics.get("plan_depth"),
            "scan_types": metrics.get("scan_types"),
            "scan_type": metrics.get("scan_type"),
            "join_strategy": metrics.get("join_strategy"),
            "relation_names": metrics.get("relation_names"),
            "analyzed": plan.meta_data.get("analyzed", False),
        }

    def detect_issues(
        self,
        plan_id: int,
        db: Session,
        cost_threshold: float = 1000.0,
    ) -> dict[str, Any]:
        """
        Detect issues in an execution plan.

        Args:
            plan_id: Execution plan ID
            db: Database session
            cost_threshold: Cost threshold for expensive nodes

        Returns:
            Dictionary with detected issues

        Raises:
            AnalysisError: If plan not found
        """
        plan = db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise AnalysisError("Execution plan not found", plan_id=plan_id)

        # Detect issues
        expensive_nodes = self.extractor.detect_expensive_nodes(plan.plan_json, cost_threshold)
        sequential_scans = self.extractor.detect_sequential_scans(plan.plan_json)
        missing_indexes = self.extractor.detect_missing_indexes(plan.plan_json)

        return {
            "plan_id": plan_id,
            "query_id": plan.query_id,
            "cost_threshold": cost_threshold,
            "expensive_nodes": expensive_nodes,
            "sequential_scans": sequential_scans,
            "missing_indexes": missing_indexes,
        }
