"""High cost detection rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class HighCostRule(DiagnosticRule):
    """Rule to detect high cost queries."""

    def __init__(
        self,
        threshold: float = 1000.0,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize high cost rule.

        Args:
            threshold: Cost threshold
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("high_cost", severity, enabled)
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
            """Check a single node for high cost."""
            total_cost = node.get("Total Cost", 0.0)
            node_type = node.get("Node Type", "")

            if total_cost >= self.threshold:
                result = DiagnosticResult(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    explanation=f"Node has a high total cost of {total_cost}, which exceeds the threshold of {self.threshold}.",
                    evidence={
                        "node_type": node_type,
                        "total_cost": total_cost,
                        "threshold": self.threshold,
                    },
                    recommendation="Consider optimizing the query by adding indexes, reducing the dataset size, or restructuring the query to reduce cost.",
                    location={
                        "node_type": node_type,
                        "path": path,
                    },
                    metadata={
                        "rule_type": "high_cost",
                        "threshold_type": "total_cost",
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
