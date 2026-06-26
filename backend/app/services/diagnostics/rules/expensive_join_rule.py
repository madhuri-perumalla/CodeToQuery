"""Expensive join detection rule."""
from typing import Any

from app.core.logging import get_logger
from app.services.diagnostics.rule_engine import DiagnosticRule, DiagnosticResult

logger = get_logger(__name__)


class ExpensiveJoinRule(DiagnosticRule):
    """Rule to detect expensive joins."""

    def __init__(
        self,
        threshold: float = 500.0,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize expensive join rule.

        Args:
            threshold: Cost threshold for joins
            severity: Rule severity
            enabled: Whether rule is enabled
        """
        super().__init__("expensive_join", severity, enabled)
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
            """Check a single node for expensive joins."""
            node_type = node.get("Node Type", "")
            total_cost = node.get("Total Cost", 0.0)

            # Check for join types
            join_types = [
                "Hash Join",
                "Merge Join",
                "Nested Loop",
                "Hash Semi Join",
                "Merge Semi Join",
                "Hash Anti Join",
                "Merge Anti Join",
            ]

            if any(join_type in node_type for join_type in join_types):
                if total_cost >= self.threshold:
                    result = DiagnosticResult(
                        rule_id=self.rule_id,
                        severity=self.severity,
                        explanation=f"Join operation '{node_type}' has a high cost of {total_cost}, which exceeds the threshold of {self.threshold}.",
                        evidence={
                            "node_type": node_type,
                            "total_cost": total_cost,
                            "threshold": self.threshold,
                        },
                        recommendation="Consider adding indexes on join columns, reducing the dataset size, or using a different join strategy to reduce cost.",
                        location={
                            "node_type": node_type,
                            "path": path,
                        },
                        metadata={
                            "rule_type": "expensive_join",
                            "threshold_type": "join_cost",
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
