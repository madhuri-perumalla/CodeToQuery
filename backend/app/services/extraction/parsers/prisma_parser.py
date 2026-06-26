"""Prisma ORM parser for Node.js/TypeScript."""
import re
from typing import Any, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class PrismaParser:
    """Parser for Prisma ORM queries."""

    # Prisma client methods
    QUERY_METHODS = [
        "findMany",
        "findFirst",
        "findUnique",
        "findFirstOrThrow",
        "findUniqueOrThrow",
        "create",
        "createMany",
        "update",
        "updateMany",
        "upsert",
        "delete",
        "deleteMany",
        "count",
        "aggregate",
        "groupBy",
    ]

    def __init__(self) -> None:
        """Initialize Prisma parser."""
        self.query_pattern = self._build_query_pattern()

    def _build_query_pattern(self) -> re.Pattern:
        """
        Build regex pattern for Prisma query detection.

        Returns:
            Compiled regex pattern
        """
        methods = "|".join(self.QUERY_METHODS)
        return re.compile(rf'\.({methods})\s*\(', re.IGNORECASE)

    def parse(self, file_path: str, content: str) -> List[dict[str, Any]]:
        """
        Parse Prisma ORM queries from file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of extracted queries
        """
        queries = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Find Prisma query method calls
            matches = self.query_pattern.finditer(line)
            for match in matches:
                method = match.group(1)
                
                # Extract the query context
                query_info = self._extract_query_info(line, method, line_num)
                if query_info:
                    queries.append(query_info)
                    logger.debug(f"Found Prisma {method} at line {line_num}")

        return queries

    def _extract_query_info(self, line: str, method: str, line_num: int) -> dict[str, Any] | None:
        """
        Extract query information from a Prisma method call.

        Args:
            line: Line of code
            method: Prisma method name
            line_num: Line number

        Returns:
            Query information dictionary or None
        """
        # Try to extract the model name
        model_match = re.search(r'(\w+)\s*\.' + re.escape(method), line)
        if not model_match:
            return None
        
        model_name = model_match.group(1)
        
        # Generate a representative SQL query based on the method
        sql = self._generate_sql_from_method(method, model_name, line)
        
        return {
            "raw_sql": f"Prisma.{method} on {model_name}",
            "normalized_sql": sql,
            "line_number": line_num,
            "source_type": "orm_prisma",
            "metadata": {
                "orm": "prisma",
                "method": method,
                "model": model_name,
            },
        }

    def _generate_sql_from_method(self, method: str, model_name: str, line: str) -> str:
        """
        Generate a representative SQL query from a Prisma method.

        Args:
            method: Prisma method name
            model_name: Model name
            line: Line of code

        Returns:
            Generated SQL query
        """
        table_name = self._to_table_name(model_name)
        
        if method in ["findMany", "findFirst", "findUnique", "findFirstOrThrow", "findUniqueOrThrow"]:
            where_clause = self._extract_where_clause(line)
            return f"SELECT * FROM {table_name} {where_clause};"
        elif method == "count":
            where_clause = self._extract_where_clause(line)
            return f"SELECT COUNT(*) FROM {table_name} {where_clause};"
        elif method == "create":
            return f"INSERT INTO {table_name} (...) VALUES (...);"
        elif method == "createMany":
            return f"INSERT INTO {table_name} (...) VALUES (...), (...);"
        elif method == "update":
            where_clause = self._extract_where_clause(line)
            return f"UPDATE {table_name} SET ... {where_clause};"
        elif method == "updateMany":
            where_clause = self._extract_where_clause(line)
            return f"UPDATE {table_name} SET ... {where_clause};"
        elif method == "upsert":
            return f"INSERT INTO {table_name} (...) VALUES (...) ON CONFLICT (...) DO UPDATE SET ...;"
        elif method == "delete":
            where_clause = self._extract_where_clause(line)
            return f"DELETE FROM {table_name} {where_clause};"
        elif method == "deleteMany":
            where_clause = self._extract_where_clause(line)
            return f"DELETE FROM {table_name} {where_clause};"
        elif method == "aggregate":
            return f"SELECT COUNT(*), SUM(...), AVG(...), MIN(...), MAX(...) FROM {table_name};"
        elif method == "groupBy":
            return f"SELECT ..., COUNT(*) FROM {table_name} GROUP BY ...;"
        else:
            return f"SELECT * FROM {table_name};"

    def _to_table_name(self, model_name: str) -> str:
        """
        Convert model name to table name.

        Args:
            model_name: Model name

        Returns:
            Table name
        """
        # Convert CamelCase to snake_case
        table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', model_name).lower()
        return table_name

    def _extract_where_clause(self, line: str) -> str:
        """
        Extract WHERE clause from line.

        Args:
            line: Line of code

        Returns:
            WHERE clause string
        """
        # Look for where: {...} or where: {...}
        where_match = re.search(r'where\s*:\s*\{([^}]*)\}', line)
        if where_match:
            conditions = where_match.group(1)
            if conditions.strip():
                return f"WHERE {conditions}"
        
        return ""
