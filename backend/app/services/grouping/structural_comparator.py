"""Structural comparator for normalized SQL AST comparison."""
import hashlib
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class StructuralComparator:
    """Compares normalized SQL AST structures for similarity."""

    def __init__(self) -> None:
        """Initialize structural comparator."""
        pass

    def compute_signature(self, normalized_sql: str) -> str:
        """
        Compute a structural signature from normalized SQL.

        Args:
            normalized_sql: Normalized SQL string

        Returns:
            SHA256 hash of normalized SQL
        """
        return hashlib.sha256(normalized_sql.encode()).hexdigest()

    def compute_ast_signature(self, ast_dict: dict[str, Any]) -> str:
        """
        Compute a structural signature from AST dictionary.

        Args:
            ast_dict: AST dictionary

        Returns:
            SHA256 hash of normalized AST structure
        """
        # Normalize AST for comparison
        normalized = self._normalize_ast(ast_dict)
        return hashlib.sha256(str(normalized).encode()).hexdigest()

    def _normalize_ast(self, ast_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize AST structure for comparison.

        Args:
            ast_dict: AST dictionary

        Returns:
            Normalized AST dictionary
        """
        if not isinstance(ast_dict, dict):
            return ast_dict

        normalized = {}
        for key, value in sorted(ast_dict.items()):
            # Skip keys that don't affect structure
            if key in ["alias", "as", "name"]:
                continue

            if isinstance(value, dict):
                normalized[key] = self._normalize_ast(value)
            elif isinstance(value, list):
                normalized[key] = [self._normalize_ast(item) if isinstance(item, dict) else item for item in value]
            else:
                normalized[key] = value

        return normalized

    def compare_signatures(self, sig1: str, sig2: str) -> bool:
        """
        Compare two structural signatures.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            True if signatures match
        """
        return sig1 == sig2

    def compute_similarity(self, sql1: str, sql2: str) -> float:
        """
        Compute similarity score between two SQL queries.

        Args:
            sql1: First SQL query
            sql2: Second SQL query

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Compute signatures
        sig1 = self.compute_signature(sql1)
        sig2 = self.compute_signature(sql2)

        # If exact match, return 1.0
        if sig1 == sig2:
            return 1.0

        # Compute token-based similarity
        tokens1 = set(self._tokenize_sql(sql1))
        tokens2 = set(self._tokenize_sql(sql2))

        if not tokens1 and not tokens2:
            return 1.0

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def _tokenize_sql(self, sql: str) -> list[str]:
        """
        Tokenize SQL query for similarity comparison.

        Args:
            sql: SQL query

        Returns:
            List of tokens
        """
        # Simple tokenization - split on whitespace and punctuation
        import re

        # Remove string literals
        sql = re.sub(r"'[^']*'", "''", sql)
        sql = re.sub(r'"[^"]*"', '""', sql)

        # Remove numeric literals
        sql = re.sub(r"\d+", "N", sql)

        # Split into tokens
        tokens = re.findall(r"\w+", sql.upper())
        return tokens

    def compare_ast_structures(self, ast1: dict[str, Any], ast2: dict[str, Any]) -> float:
        """
        Compare two AST structures.

        Args:
            ast1: First AST
            ast2: Second AST

        Returns:
            Similarity score between 0.0 and 1.0
        """
        sig1 = self.compute_ast_signature(ast1)
        sig2 = self.compute_ast_signature(ast2)

        if sig1 == sig2:
            return 1.0

        # Compute structural similarity
        return self._compute_structural_similarity(ast1, ast2)

    def _compute_structural_similarity(self, ast1: dict[str, Any], ast2: dict[str, Any]) -> float:
        """
        Compute structural similarity between two ASTs.

        Args:
            ast1: First AST
            ast2: Second AST

        Returns:
            Similarity score
        """
        if not isinstance(ast1, dict) or not isinstance(ast2, dict):
            return 0.0

        keys1 = set(ast1.keys())
        keys2 = set(ast2.keys())

        # Compare keys
        key_intersection = keys1.intersection(keys2)
        key_union = keys1.union(keys2)

        if not key_union:
            return 1.0

        key_similarity = len(key_intersection) / len(key_union)

        # Compare values for common keys
        value_similarities = []
        for key in key_intersection:
            val1 = ast1[key]
            val2 = ast2[key]

            if isinstance(val1, dict) and isinstance(val2, dict):
                value_similarities.append(self._compute_structural_similarity(val1, val2))
            elif isinstance(val1, list) and isinstance(val2, list):
                value_similarities.append(self._compare_lists(val1, val2))
            elif val1 == val2:
                value_similarities.append(1.0)
            else:
                value_similarities.append(0.0)

        value_similarity = sum(value_similarities) / len(value_similarities) if value_similarities else 0.0

        # Combine key and value similarities
        return (key_similarity + value_similarity) / 2

    def _compare_lists(self, list1: list[Any], list2: list[Any]) -> float:
        """
        Compare two lists.

        Args:
            list1: First list
            list2: Second list

        Returns:
            Similarity score
        """
        if not list1 and not list2:
            return 1.0

        if not list1 or not list2:
            return 0.0

        # Compare lengths
        length_similarity = min(len(list1), len(list2)) / max(len(list1), len(list2))

        # Compare elements
        element_similarities = []
        for i in range(min(len(list1), len(list2))):
            elem1 = list1[i]
            elem2 = list2[i]

            if isinstance(elem1, dict) and isinstance(elem2, dict):
                element_similarities.append(self._compute_structural_similarity(elem1, elem2))
            elif elem1 == elem2:
                element_similarities.append(1.0)
            else:
                element_similarities.append(0.0)

        element_similarity = sum(element_similarities) / len(element_similarities) if element_similarities else 0.0

        return (length_similarity + element_similarity) / 2

    def find_differences(self, ast1: dict[str, Any], ast2: dict[str, Any]) -> dict[str, Any]:
        """
        Find differences between two AST structures.

        Args:
            ast1: First AST
            ast2: Second AST

        Returns:
            Dictionary of differences
        """
        differences = {
            "added_keys": [],
            "removed_keys": [],
            "changed_keys": [],
        }

        if not isinstance(ast1, dict) or not isinstance(ast2, dict):
            return differences

        keys1 = set(ast1.keys())
        keys2 = set(ast2.keys())

        differences["added_keys"] = list(keys2 - keys1)
        differences["removed_keys"] = list(keys1 - keys2)

        common_keys = keys1.intersection(keys2)
        for key in common_keys:
            val1 = ast1[key]
            val2 = ast2[key]

            if val1 != val2:
                differences["changed_keys"].append(
                    {
                        "key": key,
                        "value1": val1,
                        "value2": val2,
                    }
                )

        return differences
