"""Sequelize ORM parser for Node.js."""
import re
from typing import Any, List

from app.core.logging import get_logger

logger = get_logger(__name__)


class SequelizeParser:
    """Parser for Sequelize ORM queries."""

    # Sequelize query methods
    QUERY_METHODS = [
        "findAll",
        "findOne",
        "findByPk",
        "findOrCreate",
        "findAndCountAll",
        "count",
        "create",
        "bulkCreate",
        "update",
        "destroy",
        "max",
        "min",
        "sum",
    ]

    # Sequelize operators
    OPERATORS = [
        "Op.and",
        "Op.or",
        "Op.not",
        "Op.gt",
        "Op.gte",
        "Op.lt",
        "Op.lte",
        "Op.ne",
        "Op.eq",
        "Op.like",
        "Op.iLike",
        "Op.in",
        "Op.notIn",
        "Op.between",
        "Op.notBetween",
    ]

    def __init__(self) -> None:
        """Initialize Sequelize parser."""
        self.query_pattern = self._build_query_pattern()

    def _build_query_pattern(self) -> re.Pattern:
        """
        Build regex pattern for Sequelize query detection.

        Returns:
            Compiled regex pattern
        """
        methods = "|".join(self.QUERY_METHODS)
        return re.compile(rf'\.({methods})\s*\(', re.IGNORECASE)

    def parse(self, file_path: str, content: str) -> List[dict[str, Any]]:
        """
        Parse Sequelize ORM queries from file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of extracted queries
        """
        queries = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Find Sequelize query method calls
            matches = self.query_pattern.finditer(line)
            for match in matches:
                method = match.group(1)
                
                # Extract the query context
                query_info = self._extract_query_info(line, method, line_num)
                if query_info:
                    queries.append(query_info)
                    logger.debug(f"Found Sequelize {method} at line {line_num}")

        return queries

    def _extract_query_info(self, line: str, method: str, line_num: int) -> dict[str, Any] | None:
        """
        Extract query information from a Sequelize method call.

        Args:
            line: Line of code
            method: Sequelize method name
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
            "raw_sql": f"Sequelize.{method} on {model_name}",
            "normalized_sql": sql,
            "line_number": line_num,
            "source_type": "orm_sequelize",
            "metadata": {
                "orm": "sequelize",
                "method": method,
                "model": model_name,
            },
        }

    def _generate_sql_from_method(self, method: str, model_name: str, line: str) -> str:
        """
        Generate a representative SQL query from a Sequelize method.

        Args:
            method: Sequelize method name
            model_name: Model name
            line: Line of code

        Returns:
            Generated SQL query
        """
        table_name = self._to_table_name(model_name)
        
        if method in ["findAll", "findOne", "findByPk", "findOrCreate", "findAndCountAll"]:
            where_clause = self._extract_where_clause(line)
            return f"SELECT * FROM {table_name} {where_clause};"
        elif method == "count":
            where_clause = self._extract_where_clause(line)
            return f"SELECT COUNT(*) FROM {table_name} {where_clause};"
        elif method == "create":
            return f"INSERT INTO {table_name} (...) VALUES (...);"
        elif method == "bulkCreate":
            return f"INSERT INTO {table_name} (...) VALUES (...), (...);"
        elif method == "update":
            where_clause = self._extract_where_clause(line)
            return f"UPDATE {table_name} SET ... {where_clause};"
        elif method == "destroy":
            where_clause = self._extract_where_clause(line)
            return f"DELETE FROM {table_name} {where_clause};"
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
