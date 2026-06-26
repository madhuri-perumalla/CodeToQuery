"""EXPLAIN runner service for PostgreSQL."""
from typing import Any

from app.core.errors import ExternalServiceError
from app.core.logging import get_logger
from app.services.explain.postgres_connection import postgres_connection

logger = get_logger(__name__)


class ExplainRunner:
    """Service for running PostgreSQL EXPLAIN commands."""

    def __init__(self) -> None:
        """Initialize EXPLAIN runner."""
        self.connection = postgres_connection

    def run_explain(
        self,
        query: str,
        analyze: bool = False,
        format: str = "json",
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Run EXPLAIN on a SQL query.

        Args:
            query: SQL query to explain
            analyze: Whether to use ANALYZE (actual execution)
            format: Output format (json, text, xml)
            timeout: Query timeout in seconds

        Returns:
            EXPLAIN result dictionary

        Raises:
            ExternalServiceError: If EXPLAIN execution fails
        """
        try:
            logger.info(f"Running EXPLAIN on query: {query[:100]}...")
            
            # Set statement timeout
            self.connection.execute_query(f"SET statement_timeout TO {timeout}")
            
            # Run EXPLAIN
            result = self.connection.execute_explain(query, analyze=analyze, format=format)
            
            logger.info(f"EXPLAIN completed successfully")
            return result

        except Exception as e:
            logger.error(f"EXPLAIN execution failed: {e}")
            raise ExternalServiceError("database", f"EXPLAIN execution failed: {e}") from e

    def run_explain_batch(
        self,
        queries: list[str],
        analyze: bool = False,
        format: str = "json",
        timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Run EXPLAIN on multiple queries.

        Args:
            queries: List of SQL queries
            analyze: Whether to use ANALYZE
            format: Output format
            timeout: Query timeout in seconds

        Returns:
            List of EXPLAIN results

        Raises:
            ExternalServiceError: If any EXPLAIN execution fails
        """
        results = []
        
        for i, query in enumerate(queries):
            try:
                result = self.run_explain(query, analyze=analyze, format=format, timeout=timeout)
                results.append({
                    "index": i,
                    "query": query,
                    "result": result,
                    "success": True,
                })
            except Exception as e:
                logger.error(f"EXPLAIN failed for query {i}: {e}")
                results.append({
                    "index": i,
                    "query": query,
                    "error": str(e),
                    "success": False,
                })

        return results

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful
        """
        return self.connection.test_connection()
