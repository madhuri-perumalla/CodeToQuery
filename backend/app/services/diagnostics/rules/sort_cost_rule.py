"""Sort cost diagnostic rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class SortCostRule(DiagnosticRule):
    """Rule to detect high sort costs."""

    def __init__(
        self,
        threshold: float = 200.0,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize sort cost rule.

        Args:
            threshold: Cost threshold for sort operations
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("sort_cost", severity, enabled)
        self.threshold = threshold

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
            """Check a single node for high sort costs."""
            node_type = node.get("Node Type", "")
            total_cost = node.get("Total Cost", 0.0)

            if node_type == "Sort":
                if total_cost >= self.threshold:
                    sort_key = node.get("Sort Key", [])
                    plan_rows = node.get("Plan Rows", 0)

                    result = DiagnosticResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        explanation=f"Sort operation has a high cost of {total_cost}, which exceeds the threshold of {self.threshold}. Sorting {plan_rows} rows on columns {sort_key}.",
                        evidence={
                            "node_type": node_type,
                            "total_cost": total_cost,
                            "threshold": self.threshold,
                            "sort_key": sort_key,
                            "plan_rows": plan_rows,
                        },
                        recommendation="Consider adding an index on the sort columns to avoid sorting, reducing the dataset size before sorting, or using a different query approach that doesn't require sorting.",
                        location={
                            "node_type": node_type,
                            "path": path,
                        },
                        metadata={
                            "rule_type": "sort_cost",
                            "threshold_type": "sort_cost",
                            "threshold_value": self.threshold,
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
