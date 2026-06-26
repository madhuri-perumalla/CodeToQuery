"""Python SQL parser for SQLAlchemy, Django, and raw SQL."""
import ast
import re
from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class PythonParser:
    """Parser for extracting SQL from Python files."""

    def __init__(self) -> None:
        """Initialize Python parser."""
        self.sql_keywords = [
            "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
            "TRUNCATE", "WITH", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT",
            "INNER", "OUTER", "GROUP", "ORDER", "HAVING", "UNION"
        ]

    def parse(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Parse Python file for SQL queries.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of query dictionaries
        """
        queries = []

        try:
            # Parse AST
            tree = ast.parse(content)

            # Extract raw SQL strings
            raw_queries = self._extract_raw_sql_strings(content, file_path)
            queries.extend(raw_queries)

            # Extract SQLAlchemy queries
            sqlalchemy_queries = self._extract_sqlalchemy_queries(tree, file_path)
            queries.extend(sqlalchemy_queries)

            # Extract Django queries
            django_queries = self._extract_django_queries(tree, file_path)
            queries.extend(django_queries)

        except SyntaxError as e:
            logger.error(f"Syntax error parsing Python file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")

        return queries

    def _extract_raw_sql_strings(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract raw SQL strings from Python code.

        Args:
            content: File content
            file_path: Path to the file

        Returns:
            List of query dictionaries
        """
        queries = []
        lines = content.split("\n")

        # Patterns for Python string literals
        patterns = [
            r'"""([^"]*)"""',  # Triple double quotes
            r"'''([^']*)'''",  # Triple single quotes
            r'"([^"]*)"',      # Double quotes
            r"'([^']*)'",      # Single quotes
        ]

        for line_num, line in enumerate(lines, start=1):
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    string_content = match.group(1)

                    # Check if string contains SQL keywords
                    if self._contains_sql(string_content):
                        # Clean the SQL
                        cleaned_sql = self._clean_sql(string_content)

                        if cleaned_sql:
                            queries.append({
                                "raw_sql": string_content,
                                "normalized_sql": cleaned_sql,
                                "line_number": line_num,
                                "source_type": "raw_sql",
                                "metadata": {
                                    "language": "python",
                                },
                            })

        return queries

    def _extract_sqlalchemy_queries(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract SQLAlchemy queries from AST.

        Args:
            tree: AST tree
            file_path: Path to the file

        Returns:
            List of query dictionaries
        """
        queries = []

        class SQLAlchemyVisitor(ast.NodeVisitor):
            def __init__(self, parser_instance: 'PythonParser'):
                self.parser = parser_instance
                self.queries = []
                self.current_line = 0

            def visit_Call(self, node: ast.Call) -> None:
                # Check for SQLAlchemy session.execute or text()
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'text', 'text_from']:
                        # Try to extract SQL from the argument
                        if node.args:
                            sql = self._extract_sql_from_node(node.args[0])
                            if sql and self.parser._contains_sql(sql):
                                cleaned = self.parser._clean_sql(sql)
                                if cleaned:
                                    self.queries.append({
                                        "raw_sql": sql,
                                        "normalized_sql": cleaned,
                                        "line_number": node.lineno,
                                        "source_type": "sqlalchemy",
                                        "metadata": {
                                            "language": "python",
                                            "orm": "sqlalchemy",
                                        },
                                    })
                self.generic_visit(node)

            def _extract_sql_from_node(self, node: ast.AST) -> str | None:
                """Extract SQL string from AST node."""
                if isinstance(node, ast.Str):
                    return node.s
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    return node.value
                return None

        visitor = SQLAlchemyVisitor(self)
        visitor.visit(tree)
        queries.extend(visitor.queries)

        return queries

    def _extract_django_queries(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract Django ORM queries from AST.

        Args:
            tree: AST tree
            file_path: Path to the file

        Returns:
            List of query dictionaries
        """
        queries = []

        class DjangoVisitor(ast.NodeVisitor):
            def __init__(self, parser_instance: 'PythonParser'):
                self.parser = parser_instance
                self.queries = []

            def visit_Call(self, node: ast.Call) -> None:
                # Check for Django QuerySet methods
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['raw', 'extra', 'annotate']:
                        # Try to extract SQL from the argument
                        if node.args:
                            sql = self._extract_sql_from_node(node.args[0])
                            if sql and self.parser._contains_sql(sql):
                                cleaned = self.parser._clean_sql(sql)
                                if cleaned:
                                    self.queries.append({
                                        "raw_sql": sql,
                                        "normalized_sql": cleaned,
                                        "line_number": node.lineno,
                                        "source_type": "django",
                                        "metadata": {
                                            "language": "python",
                                            "orm": "django",
                                        },
                                    })
                self.generic_visit(node)

            def _extract_sql_from_node(self, node: ast.AST) -> str | None:
                """Extract SQL string from AST node."""
                if isinstance(node, ast.Str):
                    return node.s
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    return node.value
                return None

        visitor = DjangoVisitor(self)
        visitor.visit(tree)
        queries.extend(visitor.queries)

        return queries

    def _contains_sql(self, text: str) -> bool:
        """
        Check if text contains SQL keywords.

        Args:
            text: Text to check

        Returns:
            True if text contains SQL keywords
        """
        text_upper = text.upper()
        keyword_count = sum(1 for keyword in self.sql_keywords if keyword in text_upper)
        return keyword_count >= 2

    def _clean_sql(self, sql: str) -> str:
        """
        Clean SQL string.

        Args:
            sql: SQL string to clean

        Returns:
            Cleaned SQL string
        """
        # Remove Python format strings
        sql = re.sub(r'%s', '?', sql)
        sql = re.sub(r'%d', '?', sql)
        sql = re.sub(r'\{[^}]*\}', '?', sql)
        sql = re.sub(r'%\([^)]*\)', '?', sql)

        # Remove f-string expressions
        sql = re.sub(r'\{[^}]*\}', '?', sql)

        # Normalize whitespace
        sql = " ".join(sql.split())

        return sql.strip()
