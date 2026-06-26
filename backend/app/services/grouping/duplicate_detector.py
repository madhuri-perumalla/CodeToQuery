"""Duplicate detector for SQL queries."""
from collections import defaultdict
from typing import Any

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.location import QueryLocation
from app.models.query import ExtractedQuery
from app.services.grouping.query_pattern import PatternMatch, QueryPattern
from app.services.grouping.structural_comparator import StructuralComparator

logger = get_logger(__name__)


class DuplicateDetector:
    """Detects duplicate and near-duplicate SQL queries."""

    def __init__(self) -> None:
        """Initialize duplicate detector."""
        self.comparator = StructuralComparator()

    def detect_exact_duplicates(
        self,
        queries: list[ExtractedQuery],
    ) -> dict[str, list[int]]:
        """
        Detect exact duplicate queries.

        Args:
            queries: List of extracted queries

        Returns:
            Dictionary mapping normalized SQL to list of query IDs
        """
        duplicates = defaultdict(list)

        for query in queries:
            signature = self.comparator.compute_signature(query.normalized_sql)
            duplicates[signature].append(query.id)

        # Filter out singletons
        return {sig: ids for sig, ids in duplicates.items() if len(ids) > 1}

    def detect_near_duplicates(
        self,
        queries: list[ExtractedQuery],
        similarity_threshold: float = 0.9,
    ) -> dict[str, list[tuple[int, float]]]:
        """
        Detect near-duplicate queries based on similarity.

        Args:
            queries: List of extracted queries
            similarity_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            Dictionary mapping query signature to list of (query_id, similarity) tuples
        """
        near_duplicates = defaultdict(list)
        signatures = {}

        # Compute signatures for all queries
        for query in queries:
            sig = self.comparator.compute_signature(query.normalized_sql)
            signatures[query.id] = sig

        # Compare all pairs
        for i, query1 in enumerate(queries):
            for query2 in queries[i + 1 :]:
                similarity = self.comparator.compute_similarity(query1.normalized_sql, query2.normalized_sql)

                if similarity >= similarity_threshold:
                    sig = signatures[query1.id]
                    near_duplicates[sig].append((query2.id, similarity))

        # Filter out singletons
        return {sig: matches for sig, matches in near_duplicates.items() if len(matches) > 0}

    def detect_duplicates_with_cost(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """
        Detect duplicate queries with cost information.

        Args:
            queries: List of extracted queries
            db: Database session

        Returns:
            List of QueryPattern objects for duplicates
        """
        patterns = []
        exact_duplicates = self.detect_exact_duplicates(queries)

        for signature, query_ids in exact_duplicates.items():
            # Get execution plans for these queries
            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()

            # Calculate cost statistics
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            # Get unique files
            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            # Calculate risk score
            risk_score = self._calculate_risk_score(
                query_count=len(query_ids),
                total_cost=total_cost,
                avg_cost=avg_cost,
                files_impacted=len(files_impacted),
            )

            # Determine severity
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"duplicate_{signature[:16]}",
                pattern_type="duplicate",
                pattern_signature=signature,
                query_count=len(query_ids),
                files_impacted=files_impacted,
                total_cost=total_cost,
                max_cost=max_cost,
                avg_cost=avg_cost,
                total_rows=total_rows,
                max_rows=max_rows,
                avg_rows=avg_rows,
                risk_score=risk_score,
                severity=severity,
                sample_query_id=query_ids[0],
                metadata={
                    "duplicate_type": "exact",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def detect_near_duplicates_with_cost(
        self,
        queries: list[ExtractedQuery],
        db,
        similarity_threshold: float = 0.9,
    ) -> list[QueryPattern]:
        """
        Detect near-duplicate queries with cost information.

        Args:
            queries: List of extracted queries
            db: Database session
            similarity_threshold: Minimum similarity score

        Returns:
            List of QueryPattern objects for near-duplicates
        """
        patterns = []
        near_duplicates = self.detect_near_duplicates(queries, similarity_threshold)

        for signature, matches in near_duplicates.items():
            query_ids = [mid for mid, _ in matches]

            # Get execution plans for these queries
            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()

            # Calculate cost statistics
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            # Get unique files
            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            # Calculate risk score
            risk_score = self._calculate_risk_score(
                query_count=len(query_ids),
                total_cost=total_cost,
                avg_cost=avg_cost,
                files_impacted=len(files_impacted),
            )

            # Determine severity
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"near_duplicate_{signature[:16]}",
                pattern_type="duplicate",
                pattern_signature=signature,
                query_count=len(query_ids),
                files_impacted=files_impacted,
                total_cost=total_cost,
                max_cost=max_cost,
                avg_cost=avg_cost,
                total_rows=total_rows,
                max_rows=max_rows,
                avg_rows=avg_rows,
                risk_score=risk_score,
                severity=severity,
                sample_query_id=query_ids[0],
                metadata={
                    "duplicate_type": "near",
                    "similarity_threshold": similarity_threshold,
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def get_pattern_matches(
        self,
        pattern: QueryPattern,
        queries: list[ExtractedQuery],
        db,
    ) -> list[PatternMatch]:
        """
        Get all queries matching a pattern.

        Args:
            pattern: Query pattern
            queries: List of extracted queries
            db: Database session

        Returns:
            List of PatternMatch objects
        """
        matches = []
        query_ids = pattern.meta_data.get("query_ids", [])

        for query_id in query_ids:
            query = next((q for q in queries if q.id == query_id), None)
            if not query:
                continue

            # Get execution plan
            plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query_id).first()

            # Get location
            location = db.query(QueryLocation).filter(QueryLocation.query_id == query_id).first()

            if location:
                match = PatternMatch(
                    query_id=query_id,
                    pattern_id=pattern.pattern_id,
                    similarity_score=1.0,  # Exact match for duplicates
                    cost=plan.total_cost if plan else 0.0,
                    rows=plan.total_rows if plan else 0,
                    file_path=location.file_path,
                    line_number=location.line_number,
                    function_name=location.function_name,
                )
                matches.append(match)

        return matches

    def _calculate_risk_score(
        self,
        query_count: int,
        total_cost: float,
        avg_cost: float,
        files_impacted: int,
    ) -> float:
        """
        Calculate risk score for a pattern.

        Args:
            query_count: Number of queries in pattern
            total_cost: Total cost of all queries
            avg_cost: Average cost per query
            files_impacted: Number of files impacted

        Returns:
            Risk score between 0.0 and 100.0
        """
        # Normalize factors
        query_factor = min(query_count / 10, 1.0)  # Max at 10 queries
        cost_factor = min(avg_cost / 1000.0, 1.0)  # Max at 1000 cost
        file_factor = min(files_impacted / 5, 1.0)  # Max at 5 files

        # Weighted average
        risk_score = (query_factor * 0.4 + cost_factor * 0.4 + file_factor * 0.2) * 100

        return round(risk_score, 2)

    def _determine_severity(self, risk_score: float) -> str:
        """
        Determine severity based on risk score.

        Args:
            risk_score: Risk score (0.0 to 100.0)

        Returns:
            Severity level
        """
        if risk_score >= 75:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 25:
            return "medium"
        else:
            return "low"
