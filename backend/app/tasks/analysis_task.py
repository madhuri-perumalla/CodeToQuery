"""Analysis background task."""
from app.tasks import celery_app


@celery_app.task(name="tasks.run_analysis")
def run_analysis_task(analysis_id: int) -> dict:
    """
    Run analysis task.

    Args:
        analysis_id: Analysis run ID

    Returns:
        Task result
    """
    # TODO: Implement analysis task
    # This will be implemented when analysis service is added
    return {"status": "completed", "analysis_id": analysis_id}
