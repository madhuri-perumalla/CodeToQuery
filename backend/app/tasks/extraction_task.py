"""Extraction background task."""
from sqlalchemy.orm import Session

from app.core.database import get_db_context
from app.core.logging import get_logger
from app.models.codebase import Codebase
from app.services.extraction import ExtractionService
from app.tasks import celery_app

logger = get_logger(__name__)


@celery_app.task(name="tasks.run_extraction", bind=True)
def run_extraction_task(self, codebase_id: int) -> dict:
    """
    Run extraction task.

    Args:
        codebase_id: Codebase ID

    Returns:
        Task result
    """
    logger.info(f"Starting extraction task for codebase {codebase_id}")

    def progress_callback(**kwargs):
        """Progress callback for extraction."""
        logger.info(f"Extraction progress: {kwargs}")
        # Update task state with progress
        self.update_state(
            state="PROGRESS",
            meta=kwargs,
        )

    try:
        with get_db_context() as db:
            # Get codebase
            codebase = db.query(Codebase).filter(Codebase.id == codebase_id).first()
            if not codebase:
                raise Exception(f"Codebase {codebase_id} not found")

            # Run extraction
            extraction_service = ExtractionService()
            results = extraction_service.extract_from_codebase(
                db,
                codebase,
                progress_callback=progress_callback,
            )

            logger.info(f"Extraction task completed for codebase {codebase_id}")
            return {
                "status": "completed",
                "codebase_id": codebase_id,
                "results": results,
            }

    except Exception as e:
        logger.error(f"Extraction task failed for codebase {codebase_id}: {e}")
        return {
            "status": "failed",
            "codebase_id": codebase_id,
            "error": str(e),
        }
