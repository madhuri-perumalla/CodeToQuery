"""Diagnostic service wrapper for analysis pipeline."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.diagnostic import Diagnostic
from app.models.execution_plan import ExecutionPlan
from app.services.diagnostics.rule_engine import rule_engine
from app.services.diagnostics.rule_registry import register_default_rules

logger = get_logger(__name__)


class DiagnosticService:
    """Service for running diagnostics on execution plans."""

    def __init__(self) -> None:
        """Initialize diagnostic service."""
        # Register default rules
        register_default_rules()

    def run_diagnostics(
        self,
        db: Session,
        plan: ExecutionPlan,
    ) -> dict[str, Any]:
        """
        Run diagnostics on an execution plan.

        Args:
            db: Database session
            plan: Execution plan model

        Returns:
            Dictionary with diagnostics results
        """
        try:
            logger.info(f"Running diagnostics for plan {plan.id}")

            # Run rule engine on the plan
            results = rule_engine.evaluate_plan(plan.plan_json, plan.query_id)

            # Store diagnostics in database
            diagnostics_created = 0
            for result in results:
                diagnostic = Diagnostic(
                    plan_id=plan.id,
                    rule_id=result.rule_id,
                    severity=result.severity,
                    message=result.message,
                    location=result.location,
                    evidence=result.evidence,
                    recommendation=result.recommendation,
                    metadata=result.metadata or {},
                )
                db.add(diagnostic)
                diagnostics_created += 1

            db.commit()
            logger.info(f"Created {diagnostics_created} diagnostics for plan {plan.id}")

            return {
                "plan_id": plan.id,
                "diagnostics_created": diagnostics_created,
            }

        except Exception as e:
            logger.error(f"Error running diagnostics for plan {plan.id}: {e}")
            raise
