"""Raw SQL string extractor."""
import re
from typing import List, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)


class RawSQLExtractor:
    """Extractor for raw SQL strings in code."""

    # SQL keywords to identify SQL strings
    SQL_KEYWORDS = [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "ALTER",
        "DROP",
        "TRUNCATE",
        "WITH",
        "FROM",
        "WHERE",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "GROUP",
        "ORDER",
        "HAVING",
        "UNION",
        "INTERSECT",
        "EXCEPT",
    ]

    # Patterns for different string types
    PATTERNS = [
        # Template literals (JavaScript/TypeScript)
        r'`([^`]*)`',
        # Single-quoted strings
        r"'([^']*)'",
        # Double-quoted strings
        r'"([^"]*)"',
    ]

    def __init__(self) -> None:
        """Initialize raw SQL extractor."""
        self.sql_pattern = self._build_sql_pattern()

    def _build_sql_pattern(self) -> re.Pattern:
        """
        Build regex pattern for SQL detection.

        Returns:
            Compiled regex pattern
        """
        # Create pattern that matches SQL keywords
        keyword_pattern = "|".join(self.SQL_KEYWORDS)
        return re.compile(keyword_pattern, re.IGNORECASE)

    def extract_sql_strings(self, content: str) -> List[Tuple[int, str]]:
        """
        Extract potential SQL strings from code content.

        Args:
            content: File content

        Returns:
            List of (line_number, sql_string) tuples
        """
        sql_strings: List[Tuple[int, str]] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Try each string pattern
            for pattern in self.PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    string_content = match.group(1)
                    
                    # Check if string contains SQL keywords
                    if self._contains_sql(string_content):
                        sql_strings.append((line_num, string_content))
                        logger.debug(f"Found SQL at line {line_num}: {string_content[:50]}...")

        return sql_strings

    def _contains_sql(self, text: str) -> bool:
        """
        Check if text contains SQL keywords.

        Args:
            text: Text to check

        Returns:
            True if text contains SQL keywords
        """
        # Look for SQL keywords
        matches = self.sql_pattern.findall(text)
        return len(matches) >= 2  # Require at least 2 SQL keywords

    def clean_sql(self, sql: str) -> str:
        """
        Clean SQL string by removing template literals and whitespace.

        Args:
            sql: SQL string to clean

        Returns:
            Cleaned SQL string
        """
        # Remove template literal expressions ${...}
        sql = re.sub(r'\$\{[^}]+\}', '?', sql)
        
        # Remove common JavaScript template patterns
        sql = re.sub(r'\$\{[^}]*\}', '?', sql)
        
        # Normalize whitespace
        sql = " ".join(sql.split())
        
        return sql.strip()

    def extract_queries(self, content: str) -> List[dict]:
        """
        Extract SQL queries from code content.

        Args:
            content: File content

        Returns:
            List of query dictionaries
        """
        sql_strings = self.extract_sql_strings(content)
        queries = []

        for line_num, sql_string in sql_strings:
            cleaned_sql = self.clean_sql(sql_string)
            
            if cleaned_sql:
                queries.append({
                    "raw_sql": sql_string,
                    "normalized_sql": cleaned_sql,
                    "line_number": line_num,
                    "source_type": "raw_sql",
                })

        return queries
