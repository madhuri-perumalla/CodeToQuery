"""Base diagnostic rule."""
from abc import ABC, abstractmethod
from typing import Any

from app.models.execution_plan import ExecutionPlan


class BaseRule(ABC):
    """Base class for diagnostic rules."""

    def __init__(self, rule_id: str, severity: str) -> None:
        """
        Initialize base rule.

        Args:
            rule_id: Rule identifier
            severity: Rule severity (critical, warning, info)
        """
        self.rule_id = rule_id
        self.severity = severity

    @abstractmethod
    def evaluate(self, plan: ExecutionPlan) -> list[dict[str, Any]]:
        """
        Evaluate the rule against an execution plan.

        Args:
            plan: Execution plan to evaluate

        Returns:
            List of diagnostic results
        """
        pass
