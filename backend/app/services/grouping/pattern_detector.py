"""Pattern detector for common SQL patterns."""
import re
from collections import defaultdict
from typing import Any

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.location import QueryLocation
from app.models.query import ExtractedQuery
from app.services.grouping.query_pattern import QueryPattern

logger = get_logger(__name__)


class PatternDetector:
    """Detects common and anti-patterns in SQL queries."""

    def __init__(self) -> None:
        """Initialize pattern detector."""
        self.patterns = {
            "select_star": self._detect_select_star,
            "n_plus_1": self._detect_n_plus_1,
            "missing_where": self._detect_missing_where,
            "order_by_limit": self._detect_order_by_limit,
            "join_without_index": self._detect_join_without_index,
            "subquery_in_select": self._detect_subquery_in_select,
            "large_in_list": self._detect_large_in_list,
            "like_leading_wildcard": self._detect_like_leading_wildcard,
            "or_condition": self._detect_or_condition,
            "function_on_column": self._detect_function_on_column,
        }

    def detect_patterns(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """
        Detect all patterns in queries.

        Args:
            queries: List of extracted queries
            db: Database session

        Returns:
            List of QueryPattern objects
        """
        all_patterns = []

        for pattern_name, detector in self.patterns.items():
            patterns = detector(queries, db)
            all_patterns.extend(patterns)

        return all_patterns

    def _detect_select_star(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect SELECT * patterns."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"SELECT\s+\*\s+FROM", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        # Group by signature
        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        # Create patterns for each group
        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            # Get execution plans
            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            # Get files
            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"select_star_{signature[:16]}",
                pattern_type="anti_pattern",
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
                    "pattern_name": "select_star",
                    "description": "SELECT * retrieves all columns, potentially unnecessary data",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_n_plus_1(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect N+1 query patterns."""
        patterns = []

        # Group queries by file and function
        file_function_queries = defaultdict(list)

        for query in queries:
            locations = db.query(QueryLocation).filter(QueryLocation.query_id == query.id).all()
            for loc in locations:
                key = (loc.file_path, loc.function_name or "unknown")
                file_function_queries[key].append(query)

        # Detect patterns
        for (file_path, function_name), func_queries in file_function_queries.items():
            if len(func_queries) < 2:
                continue

            # Check if queries are similar (suggesting N+1)
            from app.services.grouping.structural_comparator import StructuralComparator

            comparator = StructuralComparator()
            signatures = [comparator.compute_signature(q.normalized_sql) for q in func_queries]

            # If many similar signatures, likely N+1
            signature_counts = defaultdict(int)
            for sig in signatures:
                signature_counts[sig] += 1

            for sig, count in signature_counts.items():
                if count >= 2:
                    query_ids = [q.id for q, s in zip(func_queries, signatures) if s == sig]

                    # Get execution plans
                    plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
                    costs = [plan.total_cost for plan in plans if plan.total_cost]
                    rows = [plan.total_rows for plan in plans if plan.total_rows]

                    total_cost = sum(costs) if costs else 0.0
                    max_cost = max(costs) if costs else 0.0
                    avg_cost = total_cost / len(costs) if costs else 0.0

                    total_rows = sum(rows) if rows else 0
                    max_rows = max(rows) if rows else 0
                    avg_rows = total_rows / len(rows) if rows else 0

                    risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, 1)
                    severity = self._determine_severity(risk_score)

                    pattern = QueryPattern(
                        pattern_id=f"n_plus_1_{sig[:16]}",
                        pattern_type="anti_pattern",
                        pattern_signature=sig,
                        query_count=len(query_ids),
                        files_impacted=[file_path],
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
                            "pattern_name": "n_plus_1",
                            "description": f"N+1 query pattern in {function_name}",
                            "file_path": file_path,
                            "function_name": function_name,
                            "query_ids": query_ids,
                        },
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_missing_where(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect queries without WHERE clause."""
        patterns = []
        matching_queries = []

        for query in queries:
            # Check if it's a SELECT/UPDATE/DELETE without WHERE
            if re.search(r"(SELECT|UPDATE|DELETE)\s+.+\s+FROM", query.normalized_sql, re.IGNORECASE):
                if not re.search(r"\bWHERE\b", query.normalized_sql, re.IGNORECASE):
                    matching_queries.append(query)

        if not matching_queries:
            return patterns

        # Group by signature
        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"missing_where_{signature[:16]}",
                pattern_type="anti_pattern",
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
                    "pattern_name": "missing_where",
                    "description": "Query without WHERE clause may scan entire table",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_order_by_limit(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect ORDER BY with LIMIT patterns."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"ORDER\s+BY.*LIMIT", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"order_by_limit_{signature[:16]}",
                pattern_type="common",
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
                    "pattern_name": "order_by_limit",
                    "description": "ORDER BY with LIMIT - common pagination pattern",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_join_without_index(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect JOIN operations without proper indexing."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"JOIN", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        # Check execution plans for sequential scans in joins
        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query.id).first()
            if plan and self._has_seq_scan_in_join(plan.plan_json):
                sig = comparator.compute_signature(query.normalized_sql)
                signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"join_no_index_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "join_without_index",
                    "description": "JOIN operation with sequential scan - missing index",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _has_seq_scan_in_join(self, plan_json: dict[str, Any]) -> bool:
        """Check if plan has sequential scan in join."""
        def check_node(node: dict[str, Any]) -> bool:
            node_type = node.get("Node Type", "")
            if node_type == "Seq Scan":
                return True
            if "Plans" in node:
                return any(check_node(child) for child in node["Plans"])
            return False

        return check_node(plan_json)

    def _detect_subquery_in_select(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect subqueries in SELECT clause."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"SELECT\s+.*\(SELECT", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"subquery_select_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "subquery_in_select",
                    "description": "Subquery in SELECT clause - consider JOIN",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_large_in_list(
        self,
        queries: list[ExtractedQuery],
        db,
        threshold: int = 10,
    ) -> list[QueryPattern]:
        """Detect large IN lists."""
        patterns = []
        matching_queries = []

        for query in queries:
            # Count IN values
            in_matches = re.findall(r"IN\s*\(([^)]+)\)", query.normalized_sql, re.IGNORECASE)
            for match in in_matches:
                values = [v.strip() for v in match.split(",")]
                if len(values) >= threshold:
                    matching_queries.append(query)
                    break

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"large_in_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "large_in_list",
                    "description": f"Large IN list (>= {threshold} values) - consider temporary table",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_like_leading_wildcard(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect LIKE with leading wildcard."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"LIKE\s+['\"]%[^%]", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"like_wildcard_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "like_leading_wildcard",
                    "description": "LIKE with leading wildcard prevents index usage",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_or_condition(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect OR conditions in WHERE clause."""
        patterns = []
        matching_queries = []

        for query in queries:
            if re.search(r"WHERE\b.*\bOR\b", query.normalized_sql, re.IGNORECASE):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"or_condition_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "or_condition",
                    "description": "OR condition may prevent index usage - consider UNION",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _detect_function_on_column(
        self,
        queries: list[ExtractedQuery],
        db,
    ) -> list[QueryPattern]:
        """Detect function calls on indexed columns."""
        patterns = []
        matching_queries = []

        for query in queries:
            # Common functions on columns
            if re.search(
                r"WHERE\s+.*\b(UPPER|LOWER|TRIM|SUBSTR|DATE|YEAR|MONTH|DAY)\s*\(",
                query.normalized_sql,
                re.IGNORECASE,
            ):
                matching_queries.append(query)

        if not matching_queries:
            return patterns

        from app.services.grouping.structural_comparator import StructuralComparator

        comparator = StructuralComparator()
        signature_groups = defaultdict(list)

        for query in matching_queries:
            sig = comparator.compute_signature(query.normalized_sql)
            signature_groups[sig].append(query.id)

        for signature, query_ids in signature_groups.items():
            if len(query_ids) < 2:
                continue

            plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()
            costs = [plan.total_cost for plan in plans if plan.total_cost]
            rows = [plan.total_rows for plan in plans if plan.total_rows]

            total_cost = sum(costs) if costs else 0.0
            max_cost = max(costs) if costs else 0.0
            avg_cost = total_cost / len(costs) if costs else 0.0

            total_rows = sum(rows) if rows else 0
            max_rows = max(rows) if rows else 0
            avg_rows = total_rows / len(rows) if rows else 0

            locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()
            files_impacted = list(set(loc.file_path for loc in locations))

            risk_score = self._calculate_risk_score(len(query_ids), total_cost, avg_cost, len(files_impacted))
            severity = self._determine_severity(risk_score)

            pattern = QueryPattern(
                pattern_id=f"function_column_{signature[:16]}",
                pattern_type="expensive",
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
                    "pattern_name": "function_on_column",
                    "description": "Function on column prevents index usage - consider functional index",
                    "query_ids": query_ids,
                },
            )
            patterns.append(pattern)

        return patterns

    def _calculate_risk_score(
        self,
        query_count: int,
        total_cost: float,
        avg_cost: float,
        files_impacted: int,
    ) -> float:
        """Calculate risk score for a pattern."""
        query_factor = min(query_count / 10, 1.0)
        cost_factor = min(avg_cost / 1000.0, 1.0)
        file_factor = min(files_impacted / 5, 1.0)

        risk_score = (query_factor * 0.4 + cost_factor * 0.4 + file_factor * 0.2) * 100
        return round(risk_score, 2)

    def _determine_severity(self, risk_score: float) -> str:
        """Determine severity based on risk score."""
        if risk_score >= 75:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 25:
            return "medium"
        else:
            return "low"
