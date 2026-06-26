"""Metric extractor for EXPLAIN execution plans."""
from typing import Any

from app.core.logging import get_logger
from app.services.explain.plan_parser import PlanParser

logger = get_logger(__name__)


class MetricExtractor:
    """Extractor for metrics from EXPLAIN plans."""

    def __init__(self) -> None:
        """Initialize metric extractor."""
        self.parser = PlanParser()

    def extract_metrics(self, plan_json: dict[str, Any]) -> dict[str, Any]:
        """
        Extract metrics from EXPLAIN plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            Dictionary with extracted metrics
        """
        plan = self.parser.parse_plan(plan_json)

        metrics = {
            # Cost metrics
            "startup_cost": plan.get("startup_cost", 0.0),
            "total_cost": plan.get("total_cost", 0.0),
            
            # Row metrics
            "plan_rows": plan.get("plan_rows", 0),
            "actual_rows": plan.get("actual_rows"),
            
            # Width metrics
            "plan_width": plan.get("plan_width", 0),
            
            # Time metrics (if ANALYZE was used)
            "actual_startup_time": plan.get("actual_startup_time"),
            "actual_total_time": plan.get("actual_total_time"),
            
            # Structure metrics
            "node_count": self.parser.get_node_count(plan),
            "plan_depth": self.parser.get_plan_depth(plan),
            
            # Scan metrics
            "scan_type": self.parser.extract_scan_type(plan),
            "scan_types": self.parser.get_scan_types(plan),
            
            # Join metrics
            "join_strategy": self.parser.extract_join_strategy(plan),
            
            # Relation metrics
            "relation_name": plan.get("relation_name"),
            "relation_names": self.parser.extract_relation_names(plan),
            
            # Index metrics
            "index_name": plan.get("index_name"),
            "index_cond": plan.get("index_cond"),
            
            # Filter metrics
            "filter": plan.get("filter"),
            
            # Hash metrics
            "hash_cond": plan.get("hash_cond"),
            "hash_join_cond": plan.get("hash_join_cond"),
            
            # Parallel metrics
            "workers_planned": plan.get("workers_planned"),
            "workers_launched": plan.get("workers_launched"),
            
            # Plan hash for deduplication
            "plan_hash": self.parser.generate_plan_hash(plan),
        }

        return metrics

    def extract_nested_metrics(self, plan_json: dict[str, Any]) -> dict[str, Any]:
        """
        Extract metrics from nested execution plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            Dictionary with nested metrics
        """
        plan = self.parser.parse_plan(plan_json)

        metrics = {
            "total_cost": self.parser.calculate_total_cost(plan),
            "total_rows": self.parser.calculate_total_rows(plan),
            "node_count": self.parser.get_node_count(plan),
            "plan_depth": self.parser.get_plan_depth(plan),
            "scan_types": self.parser.get_scan_types(plan),
            "relation_names": self.parser.extract_relation_names(plan),
            "plan_hash": self.parser.generate_plan_hash(plan),
        }

        # Extract metrics from nested plans
        if "plans" in plan:
            metrics["nested_plans"] = [
                self.extract_metrics(p) for p in plan["plans"]
            ]

        return metrics

    def get_cost_breakdown(self, plan_json: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Get cost breakdown by node.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            List of node costs
        """
        costs = []

        def extract_costs_recursive(p, parent_id: str | None = None):
            node_cost = {
                "node_id": parent_id,
                "node_type": p.get("node_type"),
                "startup_cost": p.get("startup_cost", 0.0),
                "total_cost": p.get("total_cost", 0.0),
                "plan_rows": p.get("plan_rows", 0),
                "relation_name": p.get("relation_name"),
                "parent_id": parent_id,
            }
            costs.append(node_cost)

            if "plans" in p:
                for i, sub_plan in enumerate(p["plans"]):
                    extract_costs_recursive(sub_plan, f"{parent_id}-{i}" if parent_id else str(i))

        extract_costs_recursive(plan_json)
        return costs

    def get_scan_type_distribution(self, plan_json: dict[str, Any]) -> dict[str, int]:
        """
        Get distribution of scan types in the plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            Dictionary with scan type counts
        """
        scan_types = self.parser.get_scan_types(self.parser.parse_plan(plan_json))
        distribution = {}

        for scan_type in scan_types:
            distribution[scan_type] = distribution.get(scan_type, 0) + 1

        return distribution

    def detect_expensive_nodes(
        self,
        plan_json: dict[str, Any],
        cost_threshold: float = 1000.0,
    ) -> list[dict[str, Any]]:
        """
        Detect expensive nodes in the plan.

        Args:
            plan_json: EXPLAIN JSON output
            cost_threshold: Cost threshold

        Returns:
            List of expensive nodes
        """
        expensive_nodes = []

        def find_expensive_recursive(p, path: str = ""):
            node_cost = p.get("total_cost", 0.0)
            
            if node_cost >= cost_threshold:
                expensive_nodes.append({
                    "path": path,
                    "node_type": p.get("node_type"),
                    "cost": node_cost,
                    "relation_name": p.get("relation_name"),
                })

            if "plans" in p:
                for i, sub_plan in enumerate(p["plans"]):
                    find_expensive_recursive(sub_plan, f"{path}/{i}" if path else str(i))

        find_expensive_recursive(plan_json)
        return expensive_nodes

    def detect_sequential_scans(
        self,
        plan_json: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Detect sequential scans in the plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            List of sequential scan nodes
        """
        sequential_scans = []

        def find_seq_scans_recursive(p, path: str = ""):
            node_type = p.get("node_type", "")
            
            if node_type == "Seq Scan":
                sequential_scans.append({
                    "path": path,
                    "relation_name": p.get("relation_name"),
                    "plan_rows": p.get("plan_rows", 0),
                    "total_cost": p.get("total_cost", 0.0),
                })

            if "plans" in p:
                for i, sub_plan in enumerate(p["plans"]):
                    find_seq_scans_recursive(sub_plan, f"{path}/{i}" if path else str(i))

        find_seq_scans_recursive(plan_json)
        return sequential_scans

    def detect_missing_indexes(
        self,
        plan_json: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Detect potentially missing indexes.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            List of potentially missing indexes
        """
        missing_indexes = []

        def find_missing_recursive(p, path: str = ""):
            # Sequential scan on a relation without explicit filter
            if p.get("node_type") == "Seq Scan":
                relation_name = p.get("relation_name")
                filter_condition = p.get("Filter")
                
                if relation_name and not filter_condition:
                    missing_indexes.append({
                        "path": path,
                        "relation_name": relation_name,
                        "plan_rows": p.get("plan_rows", 0),
                        "total_cost": p.get("total_cost", 0.0),
                        "reason": "Sequential scan without filter",
                    })
                elif filter_condition:
                    # Check if filter is on indexed column
                    index_name = p.get("index_name")
                    if not index_name:
                        missing_indexes.append({
                            "path": path,
                            "relation_name": relation_name,
                            "filter": filter_condition,
                            "plan_rows": p.get("plan_rows", 0),
                            "total_cost": p.get("total_cost", 0.0),
                            "reason": "Filter without index",
                        })

            if "plans" in p:
                for i, sub_plan in enumerate(p["plans"]):
                    find_missing_recursive(sub_plan, f"{path}/{i}" if path else str(i))

        find_missing_recursive(plan_json)
        return missing_indexes
