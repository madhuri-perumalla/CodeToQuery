"""Code-aware diagnostics service."""
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.location import QueryLocation
from app.models.query import ExtractedQuery

logger = get_logger(__name__)


@dataclass
class SourceContext:
    """Source code context for a diagnostic."""
    file_path: str
    line_number: int
    column_number: int
    function_name: str | None
    class_name: str | None
    context_snippet: str | None
    call_stack: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "context_snippet": self.context_snippet,
            "call_stack": self.call_stack,
        }


@dataclass
class CodeAwareDiagnostic:
    """Diagnostic with source code context."""
    rule_id: str
    severity: str
    explanation: str
    evidence: dict[str, Any]
    recommendation: str
    location: dict[str, Any] | None
    metadata: dict[str, Any]
    source_context: SourceContext | None
    query_id: int | None
    plan_id: int | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "explanation": self.explanation,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "location": self.location,
            "metadata": self.meta_data,
            "source_context": self.source_context.to_dict() if self.source_context else None,
            "query_id": self.query_id,
            "plan_id": self.plan_id,
        }
        return result


class CodeAwareDiagnosticsService:
    """Service for generating code-aware diagnostics."""

    def __init__(self) -> None:
        """Initialize code-aware diagnostics service."""
        pass

    def generate_code_aware_diagnostics(
        self,
        plan_id: int,
        db: Session,
    ) -> list[CodeAwareDiagnostic]:
        """
        Generate code-aware diagnostics for an execution plan.

        Args:
            plan_id: Execution plan ID
            db: Database session

        Returns:
            List of code-aware diagnostics
        """
        # Get execution plan
        plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
        if not plan:
            logger.error(f"Execution plan {plan_id} not found")
            return []

        # Get query
        query = db.query(ExtractedQuery).filter(ExtractedQuery.id == plan.query_id).first()
        if not query:
            logger.error(f"Query {plan.query_id} not found")
            return []

        # Get source locations
        locations = db.query(QueryLocation).filter(QueryLocation.query_id == query.id).all()
        if not locations:
            logger.warning(f"No source locations found for query {query.id}")
            # Return diagnostics without source context
            return self._generate_diagnostics_without_context(plan, query)

        # Get primary location (first one)
        primary_location = locations[0]

        # Evaluate rules
        from app.services.diagnostics import rule_engine

        results = rule_engine.evaluate_all(plan.plan_json)

        # Generate code-aware diagnostics
        code_aware_diagnostics = []
        for result in results:
            code_aware_diagnostic = CodeAwareDiagnostic(
                rule_id=result.rule_id,
                severity=result.severity,
                explanation=result.explanation,
                evidence=result.evidence,
                recommendation=result.recommendation,
                location=result.location,
                metadata=result.metadata,
                source_context=SourceContext(
                    file_path=primary_location.file_path,
                    line_number=primary_location.line_number,
                    column_number=primary_location.column_number,
                    function_name=primary_location.function_name,
                    class_name=primary_location.class_name,
                    context_snippet=primary_location.context_snippet,
                    call_stack=primary_location.call_stack,
                ),
                query_id=query.id,
                plan_id=plan.id,
            )
            code_aware_diagnostics.append(code_aware_diagnostic)

        return code_aware_diagnostics

    def generate_code_aware_diagnostics_for_query(
        self,
        query_id: int,
        db: Session,
    ) -> list[CodeAwareDiagnostic]:
        """
        Generate code-aware diagnostics for a query.

        Args:
            query_id: Query ID
            db: Database session

        Returns:
            List of code-aware diagnostics
        """
        # Get query
        query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
        if not query:
            logger.error(f"Query {query_id} not found")
            return []

        # Get execution plan
        plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query_id).first()
        if not plan:
            logger.warning(f"No execution plan found for query {query_id}")
            return []

        return self.generate_code_aware_diagnostics(plan.id, db)

    def generate_code_aware_diagnostics_for_codebase(
        self,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Generate code-aware diagnostics for all queries in a codebase.

        Args:
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Dictionary with diagnostics grouped by file
        """
        # Get all queries in codebase
        queries = db.query(ExtractedQuery).filter(ExtractedQuery.codebase_id == codebase_id).all()

        diagnostics_by_file: dict[str, list[CodeAwareDiagnostic]] = {}

        for query in queries:
            # Get execution plan
            plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id == query.id).first()
            if not plan:
                continue

            # Generate diagnostics
            diagnostics = self.generate_code_aware_diagnostics(plan.id, db)

            # Group by file
            for diagnostic in diagnostics:
                if diagnostic.source_context:
                    file_path = diagnostic.source_context.file_path
                    if file_path not in diagnostics_by_file:
                        diagnostics_by_file[file_path] = []
                    diagnostics_by_file[file_path].append(diagnostic)

        return {
            "codebase_id": codebase_id,
            "total_diagnostics": sum(len(d) for d in diagnostics_by_file.values()),
            "files": diagnostics_by_file,
        }

    def _generate_diagnostics_without_context(
        self,
        plan: ExecutionPlanModel,
        query: ExtractedQuery,
    ) -> list[CodeAwareDiagnostic]:
        """
        Generate diagnostics without source context.

        Args:
            plan: Execution plan
            query: Query

        Returns:
            List of diagnostics without source context
        """
        from app.services.diagnostics import rule_engine

        results = rule_engine.evaluate_all(plan.plan_json)

        code_aware_diagnostics = []
        for result in results:
            code_aware_diagnostic = CodeAwareDiagnostic(
                rule_id=result.rule_id,
                severity=result.severity,
                explanation=result.explanation,
                evidence=result.evidence,
                recommendation=result.recommendation,
                location=result.location,
                metadata=result.meta_data,
                source_context=None,
                query_id=query.id,
                plan_id=plan.id,
            )
            code_aware_diagnostics.append(code_aware_diagnostic)

        return code_aware_diagnostics

    def get_source_context_for_query(
        self,
        query_id: int,
        db: Session,
    ) -> SourceContext | None:
        """
        Get source context for a query.

        Args:
            query_id: Query ID
            db: Database session

        Returns:
            Source context or None
        """
        # Get locations
        locations = db.query(QueryLocation).filter(QueryLocation.query_id == query_id).all()
        if not locations:
            return None

        # Return primary location
        primary_location = locations[0]
        return SourceContext(
            file_path=primary_location.file_path,
            line_number=primary_location.line_number,
            column_number=primary_location.column_number,
            function_name=primary_location.function_name,
            class_name=primary_location.class_name,
            context_snippet=primary_location.context_snippet,
            call_stack=primary_location.call_stack,
        )

    def get_source_context_for_plan(
        self,
        plan_id: int,
        db: Session,
    ) -> SourceContext | None:
        """
        Get source context for an execution plan.

        Args:
            plan_id: Execution plan ID
            db: Database session

        Returns:
            Source context or None
        """
        # Get plan
        plan = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.id == plan_id).first()
        if not plan:
            return None

        return self.get_source_context_for_query(plan.query_id, db)

    def format_diagnostic_message(
        self,
        diagnostic: CodeAwareDiagnostic,
    ) -> str:
        """
        Format a diagnostic as a human-readable message.

        Args:
            diagnostic: Code-aware diagnostic

        Returns:
            Formatted message
        """
        if diagnostic.source_context:
            location_str = f"{diagnostic.source_context.file_path}:{diagnostic.source_context.line_number}"
            if diagnostic.source_context.function_name:
                location_str += f" in {diagnostic.source_context.function_name}()"
        else:
            location_str = "Unknown location"

        return f"[{diagnostic.severity.upper()}] {location_str}: {diagnostic.explanation}"
