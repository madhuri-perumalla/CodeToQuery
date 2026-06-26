"""Full table scan diagnostic rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class FullTableScanRule(DiagnosticRule):
    """Rule to detect full table scans."""

    def __init__(
        self,
        row_threshold: int = 10000,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize full table scan rule.

        Args:
            row_threshold: Row count threshold for warning
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("full_table_scan", severity, enabled)
        self.row_threshold = row_threshold

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
            """Check a single node for sequential scans."""
            node_type = node.get("Node Type", "")

            if node_type == "Seq Scan":
                plan_rows = node.get("Plan Rows", 0)
                total_cost = node.get("Total Cost", 0.0)
                relation_name = node.get("Relation Name", "unknown")

                # Only warn if row count exceeds threshold
                if plan_rows >= self.row_threshold:
                    result = DiagnosticResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        explanation=f"PostgreSQL chose a sequential scan on table '{relation_name}' with an estimated {plan_rows} rows.",
                        evidence={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "plan_rows": plan_rows,
                            "total_cost": total_cost,
                            "row_threshold": self.row_threshold,
                        },
                        recommendation=f"Consider adding an index on frequently filtered columns of '{relation_name}' to avoid full table scans.",
                        location={
                            "node_type": node_type,
                            "relation_name": relation_name,
                            "path": path,
                        },
                        metadata={
                            "rule_type": "full_table_scan",
                            "threshold_type": "row_count",
                            "threshold_value": self.row_threshold,
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
