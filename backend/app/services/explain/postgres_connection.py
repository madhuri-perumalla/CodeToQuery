"""PostgreSQL connection management for EXPLAIN analysis."""
from typing import Any

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

from app.core.config import get_settings
from app.core.errors import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PostgreSQLConnection:
    """PostgreSQL connection manager for EXPLAIN analysis."""

    def __init__(self) -> None:
        """Initialize PostgreSQL connection manager."""
        self.settings = get_settings()
        self._connection_pool = None

    def _parse_database_url(self, url: str) -> dict[str, str]:
        """
        Parse database URL into components.

        Args:
            url: Database URL

        Returns:
            Dictionary with connection components
        """
        parsed = urlparse(url)
        
        # Extract password from netloc if present
        netloc = parsed.netloc
        if "@" in netloc:
            auth, host = netloc.split("@")
            user, password = auth.split(":")
        else:
            user = parsed.username
            password = parsed.password
            host = netloc
        
        return {
            "host": host,
            "database": parsed.path.lstrip("/"),
            "user": user,
            "password": password,
            "port": parsed.port or 5432,
        }

    def get_connection_pool(self) -> pool.SimpleConnectionPool:
        """
        Get or create connection pool.

        Returns:
            Connection pool
        """
        if self._connection_pool is None:
            db_config = self._parse_database_url(self.settings.database_url_sync)
            
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=self.settings.DATABASE_POOL_SIZE,
                **db_config
            )
        return self._connection_pool

    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Get a connection from the pool.

        Returns:
            Database connection
        """
        pool = self.get_connection_pool()
        return pool.getconn()

    def return_connection(self, connection: psycopg2.extensions.connection) -> None:
        """
        Return a connection to the pool.

        Args:
            connection: Database connection
        """
        pool = self.get_connection_pool()
        pool.putconn(connection)

    def execute_query(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
        fetch: bool = True,
    ) -> list[dict[str, Any]] | None:
        """
        Execute a query on the database.

        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results or None

        Raises:
            ExternalServiceError: If query execution fails
        """
        connection = self.get_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                connection.commit()
                return None
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise ExternalServiceError("database", f"Failed to execute query: {e}") from e
        finally:
            self.return_connection(connection)

    def execute_explain(
        self,
        query: str,
        analyze: bool = False,
        format: str = "json",
    ) -> dict[str, Any]:
        """
        Execute EXPLAIN on a query.

        Args:
            query: SQL query to explain
            analyze: Whether to use ANALYZE
            format: Output format (json, text, xml)

        Returns:
            EXPLAIN result

        Raises:
            ExternalServiceError: If EXPLAIN execution fails
        """
        explain_query = f"EXPLAIN (FORMAT {format}"
        if analyze:
            explain_query += ", ANALYZE"
        explain_query += f") {query}"

        connection = self.get_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(explain_query)
                result = cursor.fetchone()
                
                # Parse JSON result
                if format == "json" and result:
                    import json
                    return json.loads(result[0] if isinstance(result, list) else result.get("QUERY PLAN", {}))
                
                return result
        except Exception as e:
            logger.error(f"Failed to execute EXPLAIN: {e}")
            raise ExternalServiceError("database", f"Failed to execute EXPLAIN: {e}") from e
        finally:
            self.return_connection(connection)

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.return_connection(connection)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close all connections and the pool."""
        if self._connection_pool:
            self._connection_pool.closeall()
            self._connection_pool = None


# Global connection instance
postgres_connection = PostgreSQLConnection()
