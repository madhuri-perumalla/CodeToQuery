"""SQL file parser for .sql files."""
import re
from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLFileParser:
    """Parser for extracting SQL from .sql files."""

    def __init__(self) -> None:
        """Initialize SQL file parser."""
        self.statement_delimiters = [';', '\g', '\\g']
        self.sql_keywords = [
            "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
            "TRUNCATE", "WITH", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT",
            "INNER", "OUTER", "GROUP", "ORDER", "HAVING", "UNION"
        ]

    def parse(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Parse SQL file for SQL queries.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of query dictionaries
        """
        queries = []

        try:
            # Split content into statements
            statements = self._split_statements(content)

            for line_num, statement in enumerate(statements, start=1):
                # Clean the statement
                cleaned = self._clean_sql(statement)

                # Check if it's a valid SQL statement
                if cleaned and self._is_valid_sql(cleaned):
                    queries.append({
                        "raw_sql": statement,
                        "normalized_sql": cleaned,
                        "line_number": line_num,
                        "source_type": "sql_file",
                        "metadata": {
                            "file_type": "sql",
                        },
                    })

        except Exception as e:
            logger.error(f"Error parsing SQL file {file_path}: {e}")

        return queries

    def _split_statements(self, content: str) -> List[str]:
        """
        Split SQL content into individual statements.

        Args:
            content: SQL file content

        Returns:
            List of SQL statements
        """
        statements = []

        # Remove comments
        content = self._remove_comments(content)

        # Split by semicolons
        parts = content.split(';')

        for part in parts:
            # Clean and check if non-empty
            cleaned = part.strip()
            if cleaned:
                statements.append(cleaned)

        return statements

    def _remove_comments(self, content: str) -> str:
        """
        Remove SQL comments from content.

        Args:
            content: SQL content

        Returns:
            Content without comments
        """
        # Remove single-line comments (-- comment)
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)

        # Remove multi-line comments (/* comment */)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        return content

    def _clean_sql(self, sql: str) -> str:
        """
        Clean SQL string.

        Args:
            sql: SQL string to clean

        Returns:
            Cleaned SQL string
        """
        # Remove leading/trailing whitespace
        sql = sql.strip()

        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql)

        # Remove trailing semicolon
        if sql.endswith(';'):
            sql = sql[:-1].strip()

        return sql

    def _is_valid_sql(self, sql: str) -> bool:
        """
        Check if string is a valid SQL statement.

        Args:
            sql: SQL string to check

        Returns:
            True if valid SQL statement
        """
        sql_upper = sql.upper()

        # Check if it starts with a SQL keyword
        for keyword in self.sql_keywords:
            if sql_upper.startswith(keyword):
                return True

        return False
