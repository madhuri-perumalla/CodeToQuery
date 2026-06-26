"""Analysis background tasks."""
from celery import Task
from sqlalchemy.orm import Session

from app.tasks import celery_app
from app.core.database import SessionLocal
from app.models.analysis_run import AnalysisRun
from app.models.codebase import Codebase
from app.models.query import ExtractedQuery
from app.models.execution_plan import ExecutionPlan
from app.models.diagnostic import Diagnostic
from app.core.errors import AnalysisError


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db: Session | None = None

    @property
    def db(self) -> Session:
        """Get database session."""
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args: object, **kwargs: object) -> None:
        """Clean up database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.analysis_tasks.run_analysis_task')
def run_analysis_task(self: DatabaseTask, analysis_id: int) -> dict[str, object]:
    """
    Run analysis task for a codebase.

    Args:
        analysis_id: Analysis run ID

    Returns:
        Analysis results summary

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Get analysis run
        analysis = self.db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
        if not analysis:
            raise AnalysisError(f"Analysis run {analysis_id} not found")
        
        # Update status to running
        analysis.status = "running"
        self.db.commit()
        
        # Get codebase
        codebase = self.db.query(Codebase).filter(Codebase.id == analysis.codebase_id).first()
        if not codebase:
            raise AnalysisError(f"Codebase {analysis.codebase_id} not found")
        
        # Update codebase status
        codebase.status = "scanning"
        self.db.commit()
        
        # Step 1: Extract SQL queries from codebase
        from app.services.extraction.extraction_service import ExtractionService
        extraction_service = ExtractionService()

        # Update progress to 10%
        analysis.status = "running"
        analysis.meta_data = {
            **(analysis.meta_data or {}),
            "current_step": "extracting_queries",
            "progress": 10,
        }
        self.db.commit()

        try:
            extraction_results = extraction_service.extract_from_codebase(
                db=self.db,
                codebase=codebase,
            )
        except Exception as e:
            # Extraction failure is critical - mark analysis as failed
            logger.error(f"Extraction failed for codebase {codebase.id}: {e}")
            analysis.status = "failed"
            analysis.error_message = f"Extraction failed: {str(e)}"
            codebase.status = "failed"
            codebase.error_message = str(e)
            self.db.commit()
            raise AnalysisError(f"Extraction failed: {str(e)}") from e
        
        # Step 2: Generate execution plans for extracted queries
        from app.services.explain.explain_service import ExplainService
        explain_service = ExplainService()

        # Update progress to 30%
        analysis.meta_data = {
            **(analysis.meta_data or {}),
            "current_step": "generating_execution_plans",
            "progress": 30,
        }
        self.db.commit()

        queries = self.db.query(ExtractedQuery).filter(
            ExtractedQuery.codebase_id == codebase.id
        ).all()

        total_queries = len(queries)
        plans_generated = 0
        for idx, query in enumerate(queries):
            try:
                explain_service.analyze_query(
                    query_id=query.id,
                    db=self.db,
                )
                plans_generated += 1

                # Update progress incrementally (30% to 50%)
                if total_queries > 0:
                    progress = 30 + (idx / total_queries) * 20
                    analysis.meta_data = {
                        **(analysis.meta_data or {}),
                        "progress": int(progress),
                        "plans_generated": plans_generated,
                    }
                    if idx % 10 == 0:  # Update every 10 queries to avoid too many commits
                        self.db.commit()
            except Exception as e:
                # Log error but continue with other queries
                print(f"Error generating plan for query {query.id}: {e}")
                continue
        
        # Step 3: Run diagnostics on execution plans
        from app.services.diagnostics.diagnostic_service import DiagnosticService
        diagnostic_service = DiagnosticService()

        # Update progress to 50%
        analysis.meta_data = {
            **(analysis.meta_data or {}),
            "current_step": "running_diagnostics",
            "progress": 50,
        }
        self.db.commit()

        from app.models.execution_plan import ExecutionPlan
        plans = self.db.query(ExecutionPlan).join(ExtractedQuery).filter(
            ExtractedQuery.codebase_id == codebase.id
        ).all()

        total_plans = len(plans)
        diagnostics_generated = 0
        for idx, plan in enumerate(plans):
            try:
                diagnostic_service.run_diagnostics(
                    db=self.db,
                    plan=plan,
                )
                diagnostics_generated += 1

                # Update progress incrementally (50% to 70%)
                if total_plans > 0:
                    progress = 50 + (idx / total_plans) * 20
                    analysis.meta_data = {
                        **(analysis.meta_data or {}),
                        "progress": int(progress),
                        "diagnostics_generated": diagnostics_generated,
                    }
                    if idx % 10 == 0:  # Update every 10 plans to avoid too many commits
                        self.db.commit()
            except Exception as e:
                # Log error but continue with other plans
                print(f"Error running diagnostics for plan {plan.id}: {e}")
                continue
        
        # Step 4: Group similar queries
        from app.services.grouping.grouping_service import GroupingService
        grouping_service = GroupingService()

        # Update progress to 70%
        analysis.meta_data = {
            **(analysis.meta_data or {}),
            "current_step": "grouping_queries",
            "progress": 70,
        }
        self.db.commit()

        grouping_results = grouping_service.group_queries(
            db=self.db,
            codebase_id=codebase.id,
        )

        # Step 5: Generate suggestions for diagnostics
        from app.services.suggestions.suggestion_service import SuggestionService
        suggestion_service = SuggestionService()

        # Update progress to 80%
        analysis.meta_data = {
            **(analysis.meta_data or {}),
            "current_step": "generating_suggestions",
            "progress": 80,
        }
        self.db.commit()

        suggestions_generated = 0
        for idx, plan in enumerate(plans):
            try:
                # Get diagnostics for this plan
                diagnostics = self.db.query(Diagnostic).filter(Diagnostic.plan_id == plan.id).all()
                for diagnostic in diagnostics:
                    # Generate suggestions for this diagnostic
                    suggestions = suggestion_service.generate_suggestions_for_diagnostic(
                        diagnostic=diagnostic,
                        db=self.db,
                    )
                    if suggestions:
                        # Save suggestions to database
                        suggestion_service.save_suggestions_to_db(
                            diagnostic_id=diagnostic.id,
                            suggestions=suggestions,
                            db=self.db,
                        )
                        suggestions_generated += len(suggestions)

                # Update progress incrementally (80% to 90%)
                if total_plans > 0:
                    progress = 80 + (idx / total_plans) * 10
                    analysis.meta_data = {
                        **(analysis.meta_data or {}),
                        "progress": int(progress),
                        "suggestions_generated": suggestions_generated,
                    }
                    if idx % 10 == 0:  # Update every 10 plans to avoid too many commits
                        self.db.commit()
            except Exception as e:
                # Log error but continue with other plans
                print(f"Error generating suggestions for plan {plan.id}: {e}")
                continue
        
        # Update analysis completion status
        analysis.status = "completed"
        analysis.completed_at = None  # Will be set by database default
        codebase.status = "completed"
        codebase.scanned_at = None  # Will be set by database default
        codebase.meta_data = {
            **codebase.meta_data,
            "plans_generated": plans_generated,
            "diagnostics_generated": diagnostics_generated,
            "suggestions_generated": suggestions_generated,
            "groups_created": grouping_results.get("groups_created", 0),
            "current_step": "completed",
            "progress": 100,
        }

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing final analysis state: {e}")
            self.db.rollback()
            raise

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "codebase_id": analysis.codebase_id,
            "queries_extracted": extraction_results.get("stored_queries", 0),
            "plans_generated": plans_generated,
            "diagnostics_generated": diagnostics_generated,
            "suggestions_generated": suggestions_generated,
            "groups_created": grouping_results.get("groups_created", 0),
        }
        
    except Exception as e:
        # Update status to failed
        if analysis:
            analysis.status = "failed"
            analysis.error_message = str(e)
            if codebase:
                codebase.status = "failed"
                codebase.error_message = str(e)
            self.db.commit()
        
        raise AnalysisError(f"Analysis failed: {str(e)}") from e


@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.analysis_tasks.generate_execution_plan_task')
def generate_execution_plan_task(self: DatabaseTask, query_id: int) -> dict[str, object]:
    """
    Generate execution plan for a query.

    Args:
        query_id: Query ID

    Returns:
        Execution plan summary

    Raises:
        AnalysisError: If plan generation fails
    """
    try:
        query = self.db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
        if not query:
            raise AnalysisError(f"Query {query_id} not found")
        
        # Use ExplainService to generate actual execution plan
        from app.services.explain.explain_service import ExplainService
        explain_service = ExplainService()
        
        plan = explain_service.analyze_query(
            query_id=query_id,
            db=self.db,
        )
        
        return {
            "query_id": query_id,
            "plan_id": plan.id,
            "status": "completed",
        }
        
    except Exception as e:
        raise AnalysisError(f"Execution plan generation failed: {str(e)}") from e


@celery_app.task(base=DatabaseTask, bind=True, name='app.tasks.analysis_tasks.run_diagnostics_task')
def run_diagnostics_task(self: DatabaseTask, plan_id: int) -> dict[str, object]:
    """
    Run diagnostics on an execution plan.

    Args:
        plan_id: Execution plan ID

    Returns:
        Diagnostics summary

    Raises:
        AnalysisError: If diagnostics fail
    """
    try:
        plan = self.db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise AnalysisError(f"Execution plan {plan_id} not found")
        
        # Use DiagnosticService to run actual diagnostics
        from app.services.diagnostics.diagnostic_service import DiagnosticService
        diagnostic_service = DiagnosticService()
        
        results = diagnostic_service.run_diagnostics(
            db=self.db,
            plan=plan,
        )
        
        return {
            "plan_id": plan_id,
            "diagnostics_created": results.get("diagnostics_created", 0),
            "status": "completed",
        }
        
    except Exception as e:
        raise AnalysisError(f"Diagnostics failed: {str(e)}") from e
