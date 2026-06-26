"""Missing index diagnostic rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class MissingIndexRule(DiagnosticRule):
    """Rule to detect missing indexes."""

    def __init__(
        self,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize missing index rule.

        Args:
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("missing_index", severity, enabled)

    def evaluate(self, plan_json: dict[str, Any]) -> list[DiagnosticResult]:
        """
        Evaluate the rule against an execution plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            List of diagnostic results
        """
        results = []

        def check_node(node: dict[str, Any], path: str = ""):
            """Check a single node for missing indexes."""
            node_type = node.get("Node Type", "")

            # Check sequential scans without indexes
            if node_type == "Seq Scan":
                relation_name = node.get("Relation Name", "unknown")
                filter_condition = node.get("Filter")
                index_name = node.get("Index Name")

                # No index used and filter present
                if not index_name and filter_condition:
                    result = DiagnosticResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        explanation=f"Sequential scan on table '{relation_name}' with filter condition '{filter_condition}' but no index was used.",
                        evidence={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "filter": filter_condition,
                            "index_name": index_name,
                        },
                        recommendation=f"Consider adding an index on the filtered columns of '{relation_name}' to support the filter condition.",
                        location={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "path": path,
                        },
                        metadata={
                            "rule_type": "missing_index",
                            "filter_present": True,
                        },
                    )
                    results.append(result)

                # Sequential scan without filter (full table scan)
                elif not filter_condition:
                    result = DiagnosticResult(
                        rule_id=self.rule_id,
                        severity="info",  # Lower severity for full table scan without filter
                        explanation=f"Sequential scan on table '{relation_name}' without any filter condition.",
                        evidence={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "filter": filter_condition,
                        },
                        recommendation=f"Review if this full table scan is necessary. Consider adding appropriate indexes if specific data is needed.",
                        location={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "path": path,
                        },
                        metadata={
                            "rule_type": "missing_index",
                            "filter_present": False,
                        },
                    )
                    results.append(result)

            # Recursively check children
            if "Plans" in node:
                for i, child in enumerate(node["Plans"]):
                    child_path = f"{path}.{i}" if path else str(i)
                    check_node(child, child_path)

        check_node(plan_json)
        return results
