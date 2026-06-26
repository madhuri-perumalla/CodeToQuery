"""Large row estimation detection rule."""
from typing import Any

from app.models.execution_plan import ExecutionPlan
from app.services.diagnostics.rules.base_rule import BaseRule


class LargeRowEstimationRule(BaseRule):
    """Rule to detect large row estimations."""

    def __init__(self, threshold: float = 100000.0) -> None:
        """
        Initialize large row estimation rule.

        Args:
            threshold: Row estimation threshold
        """
        super().__init__("large_row_estimation_rule", "info")
        self.threshold = threshold

    def evaluate(self, plan: ExecutionPlan) -> list[dict[str, Any]]:
        """
        Evaluate large row estimation rule.

        Args:
            plan: Execution plan to evaluate

        Returns:
            List of diagnostic results
        """
        # TODO: Implement large row estimation detection
        return []
