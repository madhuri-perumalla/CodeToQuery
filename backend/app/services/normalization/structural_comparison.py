"""Structural comparison service for SQL queries."""
import hashlib
from typing import Any

import sqlglot
from sqlglot import exp

from app.core.logging import get_logger
from app.services.normalization.ast_normalizer import ASTNormalizer
from app.services.normalization.sql_parser import SQLParser

logger = get_logger(__name__)


class StructuralComparison:
    """Service for comparing SQL query structures."""

    def __init__(self, dialect: str = "postgres") -> None:
        """
        Initialize structural comparison service.

        Args:
            dialect: SQL dialect to use
        """
        self.parser = SQLParser(dialect)
        self.normalizer = ASTNormalizer(dialect)

    def compare(self, sql1: str, sql2: str) -> dict[str, Any]:
        """
        Compare two SQL queries structurally.

        Args:
            sql1: First SQL query
            sql2: Second SQL query

        Returns:
            Comparison result dictionary
        """
        try:
            # Get canonical forms
            canonical1 = self.normalizer.canonical_form(sql1)
            canonical2 = self.normalizer.canonical_form(sql2)

            # Compare canonical forms
            are_identical = canonical1 == canonical2

            # Get structural signatures
            sig1 = self.normalizer.get_structural_signature(sql1)
            sig2 = self.normalizer.get_structural_signature(sql2)

            # Compare signatures
            signatures_match = sig1 == sig2

            # Calculate similarity score
            similarity_score = self._calculate_similarity(sig1, sig2)

            return {
                "are_identical": are_identical,
                "signatures_match": signatures_match,
                "similarity_score": similarity_score,
                "canonical1": canonical1,
                "canonical2": canonical2,
                "signature1": sig1,
                "signature2": sig2,
            }

        except Exception as e:
            logger.error(f"Failed to compare queries: {e}")
            return {
                "are_identical": False,
                "signatures_match": False,
                "similarity_score": 0.0,
                "error": str(e),
            }

    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """
        Calculate similarity score between two signatures.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not sig1 or not sig2:
            return 0.0

        if sig1 == sig2:
            return 1.0

        # Use Levenshtein distance for similarity
        distance = self._levenshtein_distance(sig1, sig2)
        max_len = max(len(sig1), len(sig2))

        if max_len == 0:
            return 1.0

        similarity = 1.0 - (distance / max_len)
        return round(similarity, 4)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        # s1 is now the longer string
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def get_structure_hash(self, sql: str) -> str:
        """
        Get hash of SQL structure.

        Args:
            sql: SQL query

        Returns:
            Structure hash
        """
        signature = self.normalizer.get_structural_signature(sql)
        return hashlib.sha256(signature.encode()).hexdigest()

    def are_structurally_equivalent(self, sql1: str, sql2: str) -> bool:
        """
        Check if two queries are structurally equivalent.

        Args:
            sql1: First SQL query
            sql2: Second SQL query

        Returns:
            True if structurally equivalent
        """
        comparison = self.compare(sql1, sql2)
        return comparison["are_identical"]

    def get_differences(self, sql1: str, sql2: str) -> list[dict[str, Any]]:
        """
        Get differences between two SQL queries.

        Args:
            sql1: First SQL query
            sql2: Second SQL query

        Returns:
            List of differences
        """
        differences = []

        try:
            # Parse both queries
            ast1 = self.parser.parse(sql1)
            ast2 = self.parser.parse(sql2)

            # Compare ASTs
            diff = self._compare_asts(ast1, ast2)
            differences.extend(diff)

        except Exception as e:
            logger.error(f"Failed to get differences: {e}")
            differences.append({"type": "error", "message": str(e)})

        return differences

    def _compare_asts(self, ast1: Any, ast2: Any) -> list[dict[str, Any]]:
        """
        Compare two ASTs and return differences.

        Args:
            ast1: First AST
            ast2: Second AST

        Returns:
            List of differences
        """
        differences = []

        type1 = type(ast1).__name__
        type2 = type(ast2).__name__

        if type1 != type2:
            differences.append({
                "type": "node_type_mismatch",
                "expected": type1,
                "actual": type2,
            })
            return differences

        # Compare based on node type
        if isinstance(ast1, exp.Select):
            differences.extend(self._compare_select(ast1, ast2))
        elif isinstance(ast1, exp.Join):
            differences.extend(self._compare_join(ast1, ast2))
        elif isinstance(ast1, exp.Where):
            differences.extend(self._compare_where(ast1, ast2))

        return differences

    def _compare_select(self, select1: Any, select2: Any) -> list[dict[str, Any]]:
        """
        Compare two SELECT nodes.

        Args:
            select1: First SELECT node
            select2: Second SELECT node

        Returns:
            List of differences
        """
        differences = []

        # Compare number of expressions
        if len(select1.expressions or []) != len(select2.expressions or []):
            differences.append({
                "type": "expression_count_mismatch",
                "expected": len(select1.expressions or []),
                "actual": len(select2.expressions or []),
            })

        # Compare FROM clause
        if (select1.from_ is None) != (select2.from_ is None):
            differences.append({
                "type": "from_clause_mismatch",
                "expected": select1.from_ is not None,
                "actual": select2.from_ is not None,
            })

        # Compare WHERE clause
        if (select1.where is None) != (select2.where is None):
            differences.append({
                "type": "where_clause_mismatch",
                "expected": select1.where is not None,
                "actual": select2.where is not None,
            })

        return differences

    def _compare_join(self, join1: Any, join2: Any) -> list[dict[str, Any]]:
        """
        Compare two JOIN nodes.

        Args:
            join1: First JOIN node
            join2: Second JOIN node

        Returns:
            List of differences
        """
        differences = []

        # Compare join type
        if join1.kind != join2.kind:
            differences.append({
                "type": "join_type_mismatch",
                "expected": join1.kind,
                "actual": join2.kind,
            })

        return differences

    def _compare_where(self, where1: Any, where2: Any) -> list[dict[str, Any]]:
        """
        Compare two WHERE nodes.

        Args:
            where1: First WHERE node
            where2: Second WHERE node

        Returns:
            List of differences
        """
        differences = []

        # Compare WHERE conditions
        sig1 = self.normalizer.get_structural_signature(where1.sql())
        sig2 = self.normalizer.get_structural_signature(where2.sql())

        if sig1 != sig2:
            differences.append({
                "type": "where_condition_mismatch",
                "expected": sig1,
                "actual": sig2,
            })

        return differences
