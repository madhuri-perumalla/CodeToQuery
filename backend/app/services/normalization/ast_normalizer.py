"""AST normalizer for SQL queries."""
import re
from typing import Any

import sqlglot
from sqlglot import exp

from app.core.logging import get_logger
from app.services.normalization.sql_parser import SQLParser

logger = get_logger(__name__)


class ASTNormalizer:
    """Normalizer for SQL AST structures."""

    def __init__(self, dialect: str = "postgres") -> None:
        """
        Initialize AST normalizer.

        Args:
            dialect: SQL dialect to use
        """
        self.parser = SQLParser(dialect)
        self.placeholder_counter = 0

    def normalize(self, sql: str) -> str:
        """
        Normalize SQL query.

        Args:
            sql: SQL string to normalize

        Returns:
            Normalized SQL string
        """
        try:
            # Parse SQL to AST
            ast = self.parser.parse(sql)
            
            # Normalize AST
            normalized_ast = self._normalize_ast(ast)
            
            # Convert back to SQL
            normalized_sql = normalized_ast.sql(dialect=self.parser.dialect)
            
            # Post-process normalization
            normalized_sql = self._post_process(normalized_sql)
            
            return normalized_sql

        except Exception as e:
            logger.error(f"Failed to normalize SQL: {e}")
            # Return original SQL if normalization fails
            return sql

    def _normalize_ast(self, ast: exp.Expression) -> exp.Expression:
        """
        Normalize AST structure.

        Args:
            ast: AST expression

        Returns:
            Normalized AST expression
        """
        self.placeholder_counter = 0
        return ast.copy()

    def _normalize_literal(self, literal: exp.Literal) -> exp.Placeholder:
        """
        Normalize literal to placeholder.

        Args:
            literal: Literal expression

        Returns:
            Placeholder expression
        """
        self.placeholder_counter += 1
        return exp.Placeholder(this=f"param_{self.placeholder_counter}")

    def _normalize_number(self, number: Any) -> exp.Placeholder:
        """
        Normalize number to placeholder.

        Args:
            number: Number expression

        Returns:
            Placeholder expression
        """
        self.placeholder_counter += 1
        return exp.Placeholder(this=f"param_{self.placeholder_counter}")

    def _normalize_string(self, string: exp.Literal) -> exp.Placeholder:
        """
        Normalize string literal to placeholder.

        Args:
            string: String literal expression

        Returns:
            Placeholder expression
        """
        self.placeholder_counter += 1
        return exp.Placeholder(this=f"param_{self.placeholder_counter}")

    def _normalize_boolean(self, boolean: exp.Boolean) -> exp.Placeholder:
        """
        Normalize boolean to placeholder.

        Args:
            boolean: Boolean expression

        Returns:
            Placeholder expression
        """
        self.placeholder_counter += 1
        return exp.Placeholder(this=f"param_{self.placeholder_counter}")

    def _post_process(self, sql: str) -> str:
        """
        Post-process normalized SQL.

        Args:
            sql: Normalized SQL string

        Returns:
            Post-processed SQL string
        """
        # Normalize whitespace
        sql = " ".join(sql.split())
        
        # Normalize case for keywords
        sql = self._normalize_keywords(sql)
        
        # Remove trailing semicolon
        sql = sql.rstrip(";")
        
        return sql.strip()

    def _normalize_keywords(self, sql: str) -> str:
        """
        Normalize SQL keywords to uppercase.

        Args:
            sql: SQL string

        Returns:
            SQL with normalized keywords
        """
        # Common SQL keywords
        keywords = [
            "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
            "ON", "AND", "OR", "NOT", "IN", "EXISTS", "BETWEEN", "LIKE",
            "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "INSERT",
            "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE",
            "UNION", "INTERSECT", "EXCEPT", "WITH", "AS", "DISTINCT",
            "COUNT", "SUM", "AVG", "MIN", "MAX", "CASE", "WHEN", "THEN", "ELSE", "END",
            "JOIN", "CROSS", "NATURAL", "FULL", "USING", "ASC", "DESC",
            "NULL", "IS", "TRUE", "FALSE",
        ]
        
        # Case-insensitive keyword normalization
        for keyword in keywords:
            # Use word boundaries to avoid replacing within identifiers
            pattern = r'\b' + keyword + r'\b'
            sql = re.sub(pattern, keyword, sql, flags=re.IGNORECASE)
        
        return sql

    def remove_literals(self, sql: str) -> str:
        """
        Remove literal values from SQL.

        Args:
            sql: SQL string

        Returns:
            SQL with literals replaced by placeholders
        """
        try:
            ast = self.parser.parse(sql)
            
            # Transform literals to placeholders
            def transform(node):
                if isinstance(node, exp.Literal):
                    if isinstance(node.this, (int, float)):
                        return self._normalize_number(node)
                    elif isinstance(node.this, str):
                        return self._normalize_string(node)
                    elif isinstance(node.this, bool):
                        return self._normalize_boolean(node)
                return node
            
            normalized_ast = ast.transform(transform)
            
            return normalized_ast.sql(dialect=self.parser.dialect)

        except Exception as e:
            logger.error(f"Failed to remove literals: {e}")
            return sql

    def remove_parameters(self, sql: str) -> str:
        """
        Remove parameter values and standardize placeholders.

        Args:
            sql: SQL string

        Returns:
            SQL with standardized placeholders
        """
        # Replace various parameter formats with standard placeholder
        sql = re.sub(r'\$\d+', '?', sql)  # PostgreSQL $1, $2
        sql = re.sub(r'\?', '?', sql)  # Standard ?
        sql = re.sub(r'%s', '?', sql)  # Python %s
        sql = re.sub(r':\w+', '?', sql)  # Named parameters :name
        sql = re.sub(r'\$\{\w+\}', '?', sql)  # Template literals ${name}
        
        return sql

    def normalize_aliases(self, sql: str) -> str:
        """
        Normalize table and column aliases.

        Args:
            sql: SQL string

        Returns:
            SQL with normalized aliases
        """
        try:
            ast = self.parser.parse(sql)
            
            # Transform aliases to standard format
            def transform(node):
                if isinstance(node, exp.Alias):
                    # Keep alias but normalize the name
                    if node.alias:
                        node.alias = f"alias_{hash(node.alias) % 1000}"
                return node
            
            normalized_ast = ast.transform(transform)
            
            return normalized_ast.sql(dialect=self.parser.dialect)

        except Exception as e:
            logger.error(f"Failed to normalize aliases: {e}")
            return sql

    def canonical_form(self, sql: str) -> str:
        """
        Generate canonical form of SQL for comparison.

        Args:
            sql: SQL string

        Returns:
            Canonical SQL string
        """
        # Remove literals
        sql = self.remove_literals(sql)
        
        # Remove parameters
        sql = self.remove_parameters(sql)
        
        # Normalize aliases
        sql = self.normalize_aliases(sql)
        
        # Normalize formatting
        sql = self.normalize(sql)
        
        return sql

    def get_structural_signature(self, sql: str) -> str:
        """
        Get structural signature of SQL query.

        Args:
            sql: SQL string

        Returns:
            Structural signature string
        """
        try:
            ast = self.parser.parse(sql)
            
            # Generate structural representation
            signature = self._ast_to_signature(ast)
            
            return signature

        except Exception as e:
            logger.error(f"Failed to generate signature: {e}")
            return ""

    def _ast_to_signature(self, ast: exp.Expression) -> str:
        """
        Convert AST to structural signature.

        Args:
            ast: AST expression

        Returns:
            Structural signature string
        """
        def node_to_sig(node):
            if node is None:
                return ""
            
            node_type = type(node).__name__
            
            # For literals, use generic type
            if isinstance(node, exp.Literal):
                return "LITERAL"
            elif isinstance(node, exp.Column):
                this_sig = node_to_sig(node.this)
                return "COLUMN(" + this_sig + ")"
            elif isinstance(node, exp.Table):
                this_sig = node_to_sig(node.this)
                return "TABLE(" + this_sig + ")"
            elif isinstance(node, exp.Select):
                parts = ["SELECT"]
                if node.expressions:
                    expr_sigs = [node_to_sig(e) for e in node.expressions]
                    joined_exprs = ",".join(expr_sigs)
                    parts.append("[" + joined_exprs + "]")
                if getattr(node, 'from', None):
                    from_sig = node_to_sig(getattr(node, 'from'))
                    parts.append("FROM[" + from_sig + "]")
                if node.where:
                    where_sig = node_to_sig(node.where)
                    parts.append("WHERE[" + where_sig + "]")
                joined_parts = ",".join(parts)
                return "SELECT(" + joined_parts + ")"
            elif isinstance(node, exp.Join):
                this_sig = node_to_sig(node.this)
                on_sig = node_to_sig(node.on)
                return "JOIN(" + this_sig + "," + on_sig + ")"
            elif isinstance(node, exp.Where):
                this_sig = node_to_sig(node.this)
                return "WHERE(" + this_sig + ")"
            elif isinstance(node, exp.Func):
                return "FUNC(" + node.name + ")"
            elif isinstance(node, exp.Binary):
                left_sig = node_to_sig(node.left)
                right_sig = node_to_sig(node.right)
                return "BINARY(" + left_sig + "," + right_sig + ")"
            elif isinstance(node, exp.EQ):
                return "EQ"
            elif isinstance(node, exp.NEQ):
                return "NEQ"
            elif isinstance(node, exp.GT):
                return "GT"
            elif isinstance(node, exp.GTE):
                return "GTE"
            elif isinstance(node, exp.LT):
                return "LT"
            elif isinstance(node, exp.LTE):
                return "LTE"
            elif isinstance(node, exp.And):
                return "AND"
            elif isinstance(node, exp.Or):
                return "OR"
            elif isinstance(node, exp.Not):
                return "NOT"
            elif isinstance(node, exp.In):
                this_sig = node_to_sig(node.this)
                return "IN(" + this_sig + ")"
            else:
                return node_type
        
        return node_to_sig(ast)
