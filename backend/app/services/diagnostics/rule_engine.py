"""Diagnostic rule engine."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DiagnosticResult:
    """Result of a diagnostic rule evaluation."""
    rule_id: str
    severity: str  # critical, warning, info
    explanation: str
    evidence: dict[str, Any]
    recommendation: str
    location: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "explanation": self.explanation,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "location": self.location,
            "metadata": self.meta_data,
        }


class DiagnosticRule(ABC):
    """Base class for diagnostic rules."""

    def __init__(
        self,
        rule_id: str,
        severity: str = "warning",
        enabled: bool = True,
    ) -> None:
        """
        Initialize diagnostic rule.

        Args:
            rule_id: Unique rule identifier
            severity: Rule severity (critical, warning, info)
            enabled: Whether rule is enabled
        """
        self.rule_id = rule_id
        self.severity = severity
        self.enabled = enabled

    @abstractmethod
    def evaluate(self, plan_json: dict[str, Any]) -> list[DiagnosticResult]:
        """
        Evaluate the rule against an execution plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            List of diagnostic results
        """
        pass

    def check_enabled(self) -> bool:
        """
        Check if rule is enabled.

        Returns:
            True if rule is enabled
        """
        return self.enabled

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the rule.

        Args:
            enabled: Whether to enable the rule
        """
        self.enabled = enabled


class RuleEngine:
    """Engine for managing and executing diagnostic rules."""

    def __init__(self) -> None:
        """Initialize rule engine."""
        self.rules: dict[str, DiagnosticRule] = {}

    def register_rule(self, rule: DiagnosticRule) -> None:
        """
        Register a diagnostic rule.

        Args:
            rule: Diagnostic rule to register
        """
        self.rules[rule.rule_id] = rule
        logger.info(f"Registered diagnostic rule: {rule.rule_id}")

    def unregister_rule(self, rule_id: str) -> None:
        """
        Unregister a diagnostic rule.

        Args:
            rule_id: Rule identifier
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Unregistered diagnostic rule: {rule_id}")

    def get_rule(self, rule_id: str) -> DiagnosticRule | None:
        """
        Get a registered rule.

        Args:
            rule_id: Rule identifier

        Returns:
            Diagnostic rule or None
        """
        return self.rules.get(rule_id)

    def list_rules(self) -> list[str]:
        """
        List all registered rules.

        Returns:
            List of rule identifiers
        """
        return list(self.rules.keys())

    def evaluate_all(
        self,
        plan_json: dict[str, Any],
        rule_ids: list[str] | None = None,
    ) -> list[DiagnosticResult]:
        """
        Evaluate all enabled rules against an execution plan.

        Args:
            plan_json: EXPLAIN JSON output
            rule_ids: Specific rules to evaluate (None = all)

        Returns:
            List of diagnostic results
        """
        results = []

        if rule_ids:
            rules_to_evaluate = [
                self.rules[rule_id]
                for rule_id in rule_ids
                if rule_id in self.rules and self.rules[rule_id].check_enabled()
            ]
        else:
            rules_to_evaluate = [
                rule for rule in self.rules.values() if rule.check_enabled()
            ]

        for rule in rules_to_evaluate:
            try:
                rule_results = rule.evaluate(plan_json)
                results.extend(rule_results)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

        return results

    def evaluate_rule(
        self,
        rule_id: str,
        plan_json: dict[str, Any],
    ) -> list[DiagnosticResult]:
        """
        Evaluate a specific rule against an execution plan.

        Args:
            rule_id: Rule identifier
            plan_json: EXPLAIN JSON output

        Returns:
            List of diagnostic results

        Raises:
            ValueError: If rule not found
        """
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        if not rule.check_enabled():
            return []

        return rule.evaluate(plan_json)

    def enable_rule(self, rule_id: str) -> None:
        """
        Enable a rule.

        Args:
            rule_id: Rule identifier

        Raises:
            ValueError: If rule not found
        """
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        rule.set_enabled(True)
        logger.info(f"Enabled rule: {rule_id}")

    def disable_rule(self, rule_id: str) -> None:
        """
        Disable a rule.

        Args:
            rule_id: Rule identifier

        Raises:
            ValueError: If rule not found
        """
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        rule.set_enabled(False)
        logger.info(f"Disabled rule: {rule_id}")

    def get_rule_status(self) -> dict[str, dict[str, Any]]:
        """
        Get status of all rules.

        Returns:
            Dictionary with rule status
        """
        status = {}
        for rule_id, rule in self.rules.items():
            status[rule_id] = {
                "rule_id": rule.rule_id,
                "severity": rule.severity,
                "enabled": rule.check_enabled(),
            }
        return status


# Global rule engine instance
rule_engine = RuleEngine()
