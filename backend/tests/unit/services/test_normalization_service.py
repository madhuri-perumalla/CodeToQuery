"""Tests for SQL normalization service."""
import pytest

from app.services.normalization.ast_normalizer import ASTNormalizer
from app.services.normalization.sql_parser import SQLParser
from app.services.normalization.structural_comparison import StructuralComparison
from app.services.normalization.duplicate_detector import DuplicateDetector


class TestSQLParser:
    """Tests for SQLParser."""

    def test_parse_simple_select(self):
        """Test parsing simple SELECT."""
        parser = SQLParser()
        ast = parser.parse("SELECT * FROM users")
        assert ast is not None

    def test_parse_with_where(self):
        """Test parsing SELECT with WHERE."""
        parser = SQLParser()
        ast = parser.parse("SELECT * FROM users WHERE id = 1")
        assert ast is not None

    def test_validate_valid_sql(self):
        """Test validating valid SQL."""
        parser = SQLParser()
        assert parser.validate("SELECT * FROM users") is True

    def test_validate_invalid_sql(self):
        """Test validating invalid SQL."""
        parser = SQLParser()
        assert parser.validate("INVALID SQL") is False


class TestASTNormalizer:
    """Tests for ASTNormalizer."""

    def test_normalize_simple_select(self):
        """Test normalizing simple SELECT."""
        normalizer = ASTNormalizer()
        sql = "select * from users"
        normalized = normalizer.normalize(sql)
        assert "SELECT" in normalized
        assert "FROM" in normalized

    def test_remove_literals(self):
        """Test removing literals."""
        normalizer = ASTNormalizer()
        sql = "SELECT * FROM users WHERE id = 1"
        cleaned = normalizer.remove_literals(sql)
        assert "1" not in cleaned

    def test_remove_parameters(self):
        """Test removing parameters."""
        normalizer = ASTNormalizer()
        sql = "SELECT * FROM users WHERE id = $1"
        cleaned = normalizer.remove_parameters(sql)
        assert "$1" not in cleaned
        assert "?" in cleaned

    def test_canonical_form(self):
        """Test canonical form generation."""
        normalizer = ASTNormalizer()
        sql1 = "SELECT * FROM users WHERE id = 1"
        sql2 = "SELECT * FROM users WHERE id = 100"
        canonical1 = normalizer.canonical_form(sql1)
        canonical2 = normalizer.canonical_form(sql2)
        assert canonical1 == canonical2

    def test_get_structural_signature(self):
        """Test structural signature generation."""
        normalizer = ASTNormalizer()
        sql = "SELECT * FROM users WHERE id = ?"
        signature = normalizer.get_structural_signature(sql)
        assert signature is not None
        assert "SELECT" in signature


class TestStructuralComparison:
    """Tests for StructuralComparison."""

    def test_compare_identical_queries(self):
        """Test comparing identical queries."""
        comparator = StructuralComparison()
        sql1 = "SELECT * FROM users WHERE id = 1"
        sql2 = "SELECT * FROM users WHERE id = 1"
        result = comparator.compare(sql1, sql2)
        assert result["are_identical"] is True
        assert result["similarity_score"] == 1.0

    def test_compare_structurally_identical(self):
        """Test comparing structurally identical queries."""
        comparator = StructuralComparison()
        sql1 = "SELECT * FROM users WHERE id = 1"
        sql2 = "SELECT * FROM users WHERE id = 100"
        result = comparator.compare(sql1, sql2)
        assert result["are_identical"] is True
        assert result["similarity_score"] == 1.0

    def test_compare_different_queries(self):
        """Test comparing different queries."""
        comparator = StructuralComparison()
        sql1 = "SELECT * FROM users"
        sql2 = "SELECT * FROM posts"
        result = comparator.compare(sql1, sql2)
        assert result["are_identical"] is False
        assert result["similarity_score"] < 1.0

    def test_get_structure_hash(self):
        """Test structure hash generation."""
        comparator = StructuralComparison()
        sql = "SELECT * FROM users WHERE id = ?"
        hash1 = comparator.get_structure_hash(sql)
        hash2 = comparator.get_structure_hash(sql)
        assert hash1 == hash2

    def test_are_structurally_equivalent(self):
        """Test structural equivalence check."""
        comparator = StructuralComparison()
        sql1 = "SELECT * FROM users WHERE id = 1"
        sql2 = "SELECT * FROM users WHERE id = 100"
        assert comparator.are_structurally_equivalent(sql1, sql2) is True


class TestDuplicateDetector:
    """Tests for DuplicateDetector."""

    def test_exact_duplicate_detection(self):
        """Test exact duplicate detection logic."""
        detector = DuplicateDetector()
        # This would require database setup, so we test the logic separately
        assert detector is not None

    def test_similarity_calculation(self):
        """Test similarity calculation."""
        comparator = StructuralComparison()
        sig1 = "SELECT(LITERAL)"
        sig2 = "SELECT(LITERAL)"
        similarity = comparator._calculate_similarity(sig1, sig2)
        assert similarity == 1.0

    def test_similarity_different(self):
        """Test similarity calculation for different strings."""
        comparator = StructuralComparison()
        sig1 = "SELECT(LITERAL)"
        sig2 = "SELECT(DIFFERENT)"
        similarity = comparator._calculate_similarity(sig1, sig2)
        assert similarity < 1.0
        assert similarity > 0.0

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        comparator = StructuralComparison()
        distance = comparator._levenshtein_distance("kitten", "sitting")
        assert distance == 3  # kitten -> sitten -> sittin -> sitting

    def test_levenshtein_distance_identical(self):
        """Test Levenshtein distance for identical strings."""
        comparator = StructuralComparison()
        distance = comparator._levenshtein_distance("test", "test")
        assert distance == 0
