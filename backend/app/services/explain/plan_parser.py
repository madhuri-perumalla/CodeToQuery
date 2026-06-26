"""EXPLAIN plan parser for PostgreSQL execution plans."""
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class PlanParser:
    """Parser for PostgreSQL EXPLAIN JSON output."""

    def __init__(self) -> None:
        """Initialize plan parser."""
        pass

    def parse_plan(self, plan_json: dict[str, Any]) -> dict[str, Any]:
        """
        Parse EXPLAIN JSON output.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            Parsed plan dictionary with metrics
        """
        if not plan_json:
            return {}

        # Extract top-level metrics
        parsed = {
            "plan_json": plan_json,
            "node_type": plan_json.get("Node Type", ""),
            "startup_cost": plan_json.get("Startup Cost", 0.0),
            "total_cost": plan_json.get("Total Cost", 0.0),
            "plan_rows": plan_json.get("Plan Rows", 0),
            "plan_width": plan_json.get("Plan Width", 0),
            "actual_startup_time": plan_json.get("Actual Startup Time"),
            "actual_total_time": plan_json.get("Actual Total Time"),
            "actual_loops": plan_json.get("Actual Loops"),
            "actual_rows": plan_json.get("Actual Rows"),
        }

        # Extract relation information
        parsed["relation_name"] = plan_json.get("Relation Name")
        parsed["alias"] = plan_json.get("Alias")
        parsed["schema"] = plan_json.get("Schema")

        # Extract scan information
        parsed["scan_direction"] = plan_json.get("Scan Direction")
        parsed["sort_key_count"] = plan_json.get("Sort Key Count")
        parsed["sort_key"] = plan_json.get("Sort Key")

        # Extract join information
        parsed["join_type"] = plan_json.get("Join Type")
        parsed["parent_relationship"] = plan_json.get("Parent Relationship")

        # Extract filter information
        parsed["filter"] = plan_json.get("Filter")
        parsed["index_name"] = plan_json.get("Index Name")
        parsed["index_cond"] = plan_json.get("Index Cond")

        # Extract hash information
        parsed["hash_cond"] = plan_json.get("Hash Cond")
        parsed["hash_join_cond"] = plan_json.get("Hash Join Cond")

        # Extract parallel information
        parsed["workers_planned"] = plan_json.get("Workers Planned")
        parsed["workers_launched"] = plan_json.get("Workers Launched")
        parsed["parallel_aware_leader_participation"] = plan_json.get("Parallel Aware Leader Participation")

        # Extract partial information
        parsed["partial_mode"] = plan_json.get("Partial Mode")
        parsed["partial_index_cond"] = plan_json.get("Partial Index Cond")

        # Process nested plans
        if "Plans" in plan_json:
            parsed["plans"] = [self.parse_plan(p) for p in plan_json["Plans"]]
        else:
            parsed["plans"] = []

        # Process CTEs
        if "CTE Name" in plan_json:
            parsed["cte_name"] = plan_json["CTE Name"]

        return parsed

    def extract_scan_type(self, plan: dict[str, Any]) -> str | None:
        """
        Extract scan type from plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Scan type (Seq Scan, Index Scan, etc.)
        """
        node_type = plan.get("node_type", "")
        
        # Map node types to scan types
        scan_types = {
            "Seq Scan": "sequential_scan",
            "Index Scan": "index_scan",
            "Index Only Scan": "index_only_scan",
            "Bitmap Index Scan": "bitmap_index_scan",
            "Bitmap Heap Scan": "bitmap_heap_scan",
            "Tid Scan": "tid_scan",
            "Function Scan": "function_scan",
            "Nested Loop": "nested_loop",
            "Merge Join": "merge_join",
            "Hash Join": "hash_join",
            "Sort": "sort",
            "Aggregate": "aggregate",
            "Hash Aggregate": "hash_aggregate",
            "Materialize": "materialize",
            "Sort Key Merge": "sort_key_merge",
            "Merge Append": "merge_append",
            "Append": "append",
        }

        return scan_types.get(node_type)

    def extract_join_strategy(self, plan: dict[str, Any]) -> str | None:
        """
        Extract join strategy from plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Join strategy (nested_loop, hash_join, merge_join, etc.)
        """
        node_type = plan.get("node_type", "")
        
        if node_type == "Nested Loop":
            return "nested_loop"
        elif node_type == "Hash Join":
            return "hash_join"
        elif node_type == "Merge Join":
            return "merge_join"
        elif node_type == "Hash Semi Join":
            return "hash_semi_join"
        elif node_type == "Merge Semi Join":
            return "merge_semi_join"
        elif node_type == "Hash Anti Join":
            return "hash_anti_join"
        elif node_type == "Merge Anti Join":
            return "merge_anti_join"

        return None

    def extract_relation_names(self, plan: dict[str, Any]) -> list[str]:
        """
        Extract all relation names from plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            List of relation names
        """
        relations = []

        def extract_recursive(p):
            if p.get("relation_name"):
                relations.append(p["relation_name"])

            # Recursively process nested plans
            if "plans" in p:
                for sub_plan in p["plans"]:
                    extract_recursive(sub_plan)

        extract_recursive(plan)
        return relations

    def calculate_total_cost(self, plan: dict[str, Any]) -> float:
        """
        Calculate total cost from plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Total cost
        """
        return plan.get("total_cost", 0.0)

    def calculate_total_rows(self, plan: dict[str, Any]) -> float:
        """
        Calculate total rows from plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Total rows
        """
        return plan.get("plan_rows", 0.0)

    def get_plan_depth(self, plan: dict[str, Any]) -> int:
        """
        Get the depth of the plan tree.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Plan depth
        """
        def get_depth(p, current_depth=0):
            max_depth = current_depth
            if "plans" in p:
                for sub_plan in p["plans"]:
                    depth = get_depth(sub_plan, current_depth + 1)
                    max_depth = max(max_depth, depth)
            return max_depth

        return get_depth(plan)

    def get_node_count(self, plan: dict[str, Any]) -> int:
        """
        Get the total number of nodes in the plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Node count
        """
        count = 1

        def count_nodes(p):
            nonlocal count
            if "plans" in p:
                for sub_plan in p["plans"]:
                    count += 1
                    count_nodes(sub_plan)

        count_nodes(plan)
        return count

    def get_scan_types(self, plan: dict[str, Any]) -> list[str]:
        """
        Get all scan types in the plan.

        Args:
            plan: Parsed plan dictionary

        Returns:
            List of scan types
        """
        scan_types = []

        def extract_scan_types_recursive(p):
            scan_type = self.extract_scan_type(p)
            if scan_type:
                scan_types.append(scan_type)

            if "plans" in p:
                for sub_plan in p["plans"]:
                    extract_scan_types_recursive(sub_plan)

        extract_scan_types_recursive(plan)
        return scan_types

    def generate_plan_hash(self, plan: dict[str, Any]) -> str:
        """
        Generate a hash for the plan structure.

        Args:
            plan: Parsed plan dictionary

        Returns:
            Plan hash
        """
        import hashlib
        import json

        # Create a canonical representation of the plan structure
        canonical = {
            "node_type": plan.get("node_type"),
            "relation_name": plan.get("relation_name"),
            "scan_type": self.extract_scan_type(plan),
        }

        # Add nested plan structure (simplified)
        if "plans" in plan:
            canonical["nested_count"] = len(plan["plans"])
            canonical["nested_types"] = [p.get("node_type") for p in plan["plans"]]

        canonical_str = json.dumps(canonical, sort_keys=True)
        return hashlib.sha256(canonical_str.encode()).hexdigest()
