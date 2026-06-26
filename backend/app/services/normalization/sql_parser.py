"""SQL parser using SQLGlot."""
from typing import Any

import sqlglot
from sqlglot import exp
from sqlglot.dialects import Postgres

from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLParser:
    """SQL parser using SQLGlot."""

    def __init__(self, dialect: str = "postgres") -> None:
        """
        Initialize SQL parser.

        Args:
            dialect: SQL dialect to use
        """
        self.dialect = dialect
        self.parser = sqlglot.Parser(dialect or Postgres)

    def parse(self, sql: str) -> exp.Expression:
        """
        Parse SQL string to AST.

        Args:
            sql: SQL string to parse

        Returns:
            Parsed AST expression

        Raises:
            ValueError: If SQL cannot be parsed
        """
        try:
            return self.parser.parse_one(sql)
        except Exception as e:
            logger.error(f"Failed to parse SQL: {e}")
            raise ValueError(f"Failed to parse SQL: {e}") from e

    def parse_multiple(self, sql: str) -> list[exp.Expression]:
        """
        Parse multiple SQL statements.

        Args:
            sql: SQL string with multiple statements

        Returns:
            List of parsed AST expressions
        """
        try:
            return list(self.parser.parse(sql))
        except Exception as e:
            logger.error(f"Failed to parse SQL: {e}")
            raise ValueError(f"Failed to parse SQL: {e}") from e

    def validate(self, sql: str) -> bool:
        """
        Validate SQL syntax.

        Args:
            sql: SQL string to validate

        Returns:
            True if SQL is valid, False otherwise
        """
        try:
            self.parse(sql)
            return True
        except Exception:
            return False

    def get_dialect(self) -> str:
        """
        Get the current dialect.

        Returns:
            Dialect name
        """
        return self.dialect
