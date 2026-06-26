"""EXPLAIN background task."""
from sqlalchemy.orm import Session

from app.core.database import get_db_context
from app.core.logging import get_logger
from app.models.query import ExtractedQuery
from app.services.explain import ExplainService
from app.tasks import celery_app

logger = get_logger(__name__)


@celery_app.task(name="tasks.run_explain", bind=True)
def run_explain_task(self, query_id: int) -> dict:
    """
    Run EXPLAIN task.

    Args:
        query_id: Query ID

    Returns:
        Task result
    """
    logger.info(f"Starting EXPLAIN task for query {query_id}")

    try:
        with get_db_context() as db:
            # Get query
            query = db.query(ExtractedQuery).filter(ExtractedQuery.id == query_id).first()
            if not query:
                raise Exception(f"Query {query_id} not found")

            # Run EXPLAIN analysis
            explain_service = ExplainService()
            execution_plan = explain_service.analyze_query(query_id, db, analyze=False)

            logger.info(f"EXPLAIN task completed for query {query_id}")
            return {
                "status": "completed",
                "query_id": query_id,
                "plan_id": execution_plan.id,
                "total_cost": float(execution_plan.total_cost) if execution_plan.total_cost else None,
                "total_rows": float(execution_plan.total_rows) if execution_plan.total_rows else None,
            }

    except Exception as e:
        logger.error(f"EXPLAIN task failed for query {query_id}: {e}")
        return {
            "status": "failed",
            "query_id": query_id,
            "error": str(e),
        }
