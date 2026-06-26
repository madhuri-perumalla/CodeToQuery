"""Tests for pattern grouping service."""
from unittest.mock import Mock, patch

import pytest

from app.services.grouping import PatternGroupingService
from app.services.grouping.query_pattern import PatternMatch, PatternStatistics, QueryPattern


class TestQueryPattern:
    """Tests for QueryPattern dataclass."""

    def test_to_dict(self):
        """Test QueryPattern to dictionary conversion."""
        pattern = QueryPattern(
            pattern_id="test_pattern",
            pattern_type="duplicate",
            pattern_signature="abc123",
            query_count=5,
            files_impacted=["file1.ts", "file2.ts"],
            total_cost=1000.0,
            max_cost=500.0,
            avg_cost=200.0,
            total_rows=10000,
            max_rows=5000,
            avg_rows=2000,
            risk_score=75.0,
            severity="high",
            sample_query_id=1,
            metadata={"test": "data"},
        )

        result = pattern.to_dict()

        assert result["pattern_id"] == "test_pattern"
        assert result["pattern_type"] == "duplicate"
        assert result["query_count"] == 5
        assert result["files_impacted"] == ["file1.ts", "file2.ts"]
        assert result["risk_score"] == 75.0


class TestPatternMatch:
    """Tests for PatternMatch dataclass."""

    def test_to_dict(self):
        """Test PatternMatch to dictionary conversion."""
        match = PatternMatch(
            query_id=1,
            pattern_id="test_pattern",
            similarity_score=1.0,
            cost=100.0,
            rows=1000,
            file_path="userService.ts",
            line_number=42,
            function_name="getUser",
        )

        result = match.to_dict()

        assert result["query_id"] == 1
        assert result["pattern_id"] == "test_pattern"
        assert result["similarity_score"] == 1.0
        assert result["file_path"] == "userService.ts"
        assert result["line_number"] == 42


class TestPatternStatistics:
    """Tests for PatternStatistics dataclass."""

    def test_to_dict(self):
        """Test PatternStatistics to dictionary conversion."""
        stats = PatternStatistics(
            total_patterns=10,
            duplicate_patterns=3,
            expensive_patterns=4,
            anti_patterns=2,
            common_patterns=1,
            total_queries_analyzed=100,
            queries_in_patterns=50,
            unique_queries=40,
            avg_queries_per_pattern=5.0,
            high_risk_patterns=3,
            medium_risk_patterns=4,
            low_risk_patterns=3,
        )

        result = stats.to_dict()

        assert result["total_patterns"] == 10
        assert result["duplicate_patterns"] == 3
        assert result["expensive_patterns"] == 4
        assert result["high_risk_patterns"] == 3


class TestPatternGroupingService:
    """Tests for PatternGroupingService."""

    def test_analyze_codebase_patterns_no_queries(self):
        """Test analyzing codebase with no queries."""
        service = PatternGroupingService()
        db = Mock()

        db.query.return_value.filter.return_value.all.return_value = []

        result = service.analyze_codebase_patterns(1, db)

        assert result["codebase_id"] == 1
        assert result["patterns"] == []
        assert result["statistics"]["total_patterns"] == 0

    def test_analyze_codebase_patterns_with_queries(self):
        """Test analyzing codebase with queries."""
        service = PatternGroupingService()
        db = Mock()

        # Mock queries
        query1 = Mock()
        query1.id = 1
        query1.normalized_sql = "SELECT * FROM users WHERE id = $1"
        query2 = Mock()
        query2.id = 2
        query2.normalized_sql = "SELECT * FROM users WHERE id = $1"

        db.query.return_value.filter.return_value.all.return_value = [query1, query2]

        # Mock duplicate detector
        with patch.object(service.duplicate_detector, "detect_duplicates_with_cost") as mock_duplicate:
            mock_duplicate.return_value = []

            # Mock pattern detector
            with patch.object(service.pattern_detector, "detect_patterns") as mock_patterns:
                mock_patterns.return_value = []

                result = service.analyze_codebase_patterns(1, db)

                assert result["codebase_id"] == 1
                assert result["total_queries"] == 2
                assert result["statistics"]["total_queries_analyzed"] == 2

    def test_get_pattern_inventory(self):
        """Test getting pattern inventory."""
        service = PatternGroupingService()
        db = Mock()

        # Mock analyze_codebase_patterns
        with patch.object(service, "analyze_codebase_patterns") as mock_analyze:
            mock_analyze.return_value = {
                "codebase_id": 1,
                "patterns": [
                    {
                        "pattern_id": "pattern1",
                        "pattern_type": "duplicate",
                        "query_count": 5,
                    },
                    {
                        "pattern_id": "pattern2",
                        "pattern_type": "expensive",
                        "query_count": 3,
                    },
                ],
                "statistics": {"total_patterns": 2},
            }

            inventory = service.get_pattern_inventory(1, db)

            assert inventory["codebase_id"] == 1
            assert "inventory" in inventory
            assert "duplicate" in inventory["inventory"]
            assert "expensive" in inventory["inventory"]
            assert len(inventory["inventory"]["duplicate"]) == 1
            assert len(inventory["inventory"]["expensive"]) == 1

    def test_get_high_risk_patterns(self):
        """Test getting high-risk patterns."""
        service = PatternGroupingService()
        db = Mock()

        # Mock analyze_codebase_patterns
        with patch.object(service, "analyze_codebase_patterns") as mock_analyze:
            mock_analyze.return_value = {
                "codebase_id": 1,
                "patterns": [
                    {
                        "pattern_id": "pattern1",
                        "risk_score": 80.0,
                    },
                    {
                        "pattern_id": "pattern2",
                        "risk_score": 60.0,
                    },
                    {
                        "pattern_id": "pattern3",
                        "risk_score": 30.0,
                    },
                ],
            }

            high_risk = service.get_high_risk_patterns(1, db, risk_threshold=50.0)

            assert high_risk["codebase_id"] == 1
            assert high_risk["risk_threshold"] == 50.0
            assert high_risk["total_high_risk"] == 2
            assert len(high_risk["patterns"]) == 2
            # Should be sorted by risk score descending
            assert high_risk["patterns"][0]["risk_score"] == 80.0
            assert high_risk["patterns"][1]["risk_score"] == 60.0

    def test_get_pattern_details_not_found(self):
        """Test getting pattern details when pattern not found."""
        service = PatternGroupingService()
        db = Mock()

        with patch.object(service, "analyze_codebase_patterns") as mock_analyze:
            mock_analyze.return_value = {
                "codebase_id": 1,
                "patterns": [],
            }

            details = service.get_pattern_details("nonexistent", 1, db)

            assert "error" in details
            assert "nonexistent" in details["error"]

    def test_get_pattern_details_found(self):
        """Test getting pattern details when pattern found."""
        service = PatternGroupingService()
        db = Mock()

        pattern_data = {
            "pattern_id": "pattern1",
            "pattern_type": "duplicate",
            "query_count": 2,
            "risk_score": 75.0,
            "metadata": {"query_ids": [1, 2]},
        }

        with patch.object(service, "analyze_codebase_patterns") as mock_analyze:
            mock_analyze.return_value = {
                "codebase_id": 1,
                "patterns": [pattern_data],
            }

            # Mock queries
            query1 = Mock()
            query1.id = 1
            query1.normalized_sql = "SELECT * FROM users"
            query2 = Mock()
            query2.id = 2
            query2.normalized_sql = "SELECT * FROM users"

            db.query.return_value.filter.return_value.all.return_value = [query1, query2]
            db.query.return_value.filter.return_value.first.return_value = None

            details = service.get_pattern_details("pattern1", 1, db)

            assert details["pattern"]["pattern_id"] == "pattern1"
            assert details["total_matches"] == 2
            assert len(details["matches"]) == 2

    def test_get_files_impacted_by_pattern(self):
        """Test getting files impacted by pattern."""
        service = PatternGroupingService()
        db = Mock()

        pattern_data = {
            "pattern_id": "pattern1",
            "metadata": {"query_ids": [1, 2]},
        }

        with patch.object(service, "get_pattern_details") as mock_details:
            mock_details.return_value = {
                "pattern": pattern_data,
                "matches": [
                    {
                        "query_id": 1,
                        "file_path": "userService.ts",
                        "cost": 100.0,
                        "rows": 1000,
                    },
                    {
                        "query_id": 2,
                        "file_path": "userService.ts",
                        "cost": 200.0,
                        "rows": 2000,
                    },
                    {
                        "query_id": 3,
                        "file_path": "postService.ts",
                        "cost": 150.0,
                        "rows": 1500,
                    },
                ],
            }

            file_impacts = service.get_files_impacted_by_pattern("pattern1", 1, db)

            assert file_impacts["pattern_id"] == "pattern1"
            assert file_impacts["total_files"] == 2
            assert len(file_impacts["file_impacts"]) == 2

    def test_calculate_refactoring_potential_duplicate(self):
        """Test calculating refactoring potential for duplicate pattern."""
        service = PatternGroupingService()
        db = Mock()

        pattern_data = {
            "pattern_id": "pattern1",
            "pattern_type": "duplicate",
            "metadata": {"query_ids": [1, 2, 3]},
        }

        with patch.object(service, "get_pattern_details") as mock_details:
            mock_details.return_value = {
                "pattern": pattern_data,
                "matches": [
                    {"cost": 100.0, "file_path": "file1.ts"},
                    {"cost": 200.0, "file_path": "file2.ts"},
                    {"cost": 150.0, "file_path": "file3.ts"},
                ],
            }

            potential = service.calculate_refactoring_potential("pattern1", 1, db)

            assert potential["pattern_id"] == "pattern1"
            assert potential["current_total_cost"] == 450.0
            assert potential["estimated_savings"] == 360.0  # 80% of 450
            assert potential["savings_percentage"] == 80.0
            assert potential["consolidation_opportunity"] is True
            assert potential["queries_affected"] == 3

    def test_calculate_refactoring_potential_expensive(self):
        """Test calculating refactoring potential for expensive pattern."""
        service = PatternGroupingService()
        db = Mock()

        pattern_data = {
            "pattern_id": "pattern1",
            "pattern_type": "expensive",
            "metadata": {"query_ids": [1, 2]},
        }

        with patch.object(service, "get_pattern_details") as mock_details:
            mock_details.return_value = {
                "pattern": pattern_data,
                "matches": [
                    {"cost": 100.0, "file_path": "file1.ts"},
                    {"cost": 200.0, "file_path": "file2.ts"},
                ],
            }

            potential = service.calculate_refactoring_potential("pattern1", 1, db)

            assert potential["pattern_id"] == "pattern1"
            assert potential["current_total_cost"] == 300.0
            assert potential["estimated_savings"] == 90.0  # 30% of 300
            assert potential["savings_percentage"] == 30.0
            assert potential["consolidation_opportunity"] is False

    def test_calculate_statistics(self):
        """Test calculating pattern statistics."""
        service = PatternGroupingService()

        queries = [Mock(id=i) for i in range(10)]

        patterns = [
            QueryPattern(
                pattern_id="pattern1",
                pattern_type="duplicate",
                pattern_signature="sig1",
                query_count=5,
                files_impacted=["file1.ts"],
                total_cost=1000.0,
                max_cost=500.0,
                avg_cost=200.0,
                total_rows=10000,
                max_rows=5000,
                avg_rows=2000,
                risk_score=80.0,
                severity="high",
                sample_query_id=1,
                metadata={"query_ids": [1, 2, 3, 4, 5]},
            ),
            QueryPattern(
                pattern_id="pattern2",
                pattern_type="expensive",
                pattern_signature="sig2",
                query_count=3,
                files_impacted=["file2.ts"],
                total_cost=500.0,
                max_cost=300.0,
                avg_cost=166.67,
                total_rows=5000,
                max_rows=3000,
                avg_rows=1666.67,
                risk_score=60.0,
                severity="medium",
                sample_query_id=6,
                metadata={"query_ids": [6, 7, 8]},
            ),
        ]

        stats = service._calculate_statistics(queries, patterns)

        assert stats.total_patterns == 2
        assert stats.duplicate_patterns == 1
        assert stats.expensive_patterns == 1
        assert stats.total_queries_analyzed == 10
        assert stats.queries_in_patterns == 8
        assert stats.unique_queries == 8
        assert stats.high_risk_patterns == 1
        assert stats.medium_risk_patterns == 1

    def test_create_empty_statistics(self):
        """Test creating empty statistics."""
        service = PatternGroupingService()

        stats = service._create_empty_statistics()

        assert stats.total_patterns == 0
        assert stats.duplicate_patterns == 0
        assert stats.expensive_patterns == 0
        assert stats.anti_patterns == 0
        assert stats.common_patterns == 0
        assert stats.total_queries_analyzed == 0
        assert stats.queries_in_patterns == 0
        assert stats.unique_queries == 0
        assert stats.avg_queries_per_pattern == 0.0
        assert stats.high_risk_patterns == 0
        assert stats.medium_risk_patterns == 0
        assert stats.low_risk_patterns == 0
