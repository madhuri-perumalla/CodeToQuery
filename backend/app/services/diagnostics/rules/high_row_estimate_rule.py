"""High row estimate diagnostic rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class HighRowEstimateRule(DiagnosticRule):
    """Rule to detect high row estimates."""

    def __init__(
        self,
        threshold: int = 100000,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize high row estimate rule.

        Args:
            threshold: Row count threshold
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("high_row_estimate", severity, enabled)
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
            """Check a single node for high row estimates."""
            plan_rows = node.get("Plan Rows", 0)
            node_type = node.get("Node Type", "")

            if plan_rows >= self.threshold:
                result = DiagnosticResult(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    explanation=f"Node has a high estimated row count of {plan_rows}, which exceeds the threshold of {self.threshold}.",
                    evidence={
                        "node_type": node_type,
                        "plan_rows": plan_rows,
                        "threshold": self.threshold,
                    },
                    recommendation="Consider adding filters to reduce the dataset size, adding indexes to improve selectivity, or reviewing the query logic to avoid processing unnecessary rows.",
                    location={
                        "node_type": node_type,
                        "path": path,
                    },
                    metadata={
                        "rule_type": "high_row_estimate",
                        "threshold_type": "row_count",
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
