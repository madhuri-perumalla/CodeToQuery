"""Tests for EXPLAIN service."""
import pytest

from app.services.explain.explain_runner import ExplainRunner
from app.services.explain.plan_parser import PlanParser
from app.services.explain.metric_extractor import MetricExtractor


class TestPlanParser:
    """Tests for PlanParser."""

    def test_parse_simple_plan(self):
        """Test parsing a simple plan."""
        parser = PlanParser()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }
        parsed = parser.parse_plan(plan_json)
        assert parsed["node_type"] == "Seq Scan"
        assert parsed["total_cost"] == 25.50
        assert parsed["plan_rows"] == 1000

    def test_parse_nested_plan(self):
        """Test parsing a nested plan."""
        parser = PlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 30.00,
            "Plan Rows": 100,
            "Plan Width": 8,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "users",
                    "Startup Cost": 0.00,
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                    "Plan Width": 4,
                },
                {
                    "Node Type": "Index Scan",
                    "Relation Name": "posts",
                    "Startup Cost": 0.00,
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                    "Plan Width": 4,
                },
            ],
        }
        parsed = parser.parse_plan(plan_json)
        assert parsed["node_type"] == "Hash Join"
        assert len(parsed["plans"]) == 2
        assert parsed["plans"][0]["node_type"] == "Seq Scan"
        assert parsed["plans"][1]["node_type"] == "Index Scan"

    def test_extract_scan_type(self):
        """Test scan type extraction."""
        parser = PlanParser()
        plan = {
            "node_type": "Seq Scan",
            "relation_name": "users",
        }
        scan_type = parser.extract_scan_type(plan)
        assert scan_type == "sequential_scan"

    def test_extract_join_strategy(self):
        """Test join strategy extraction."""
        parser = PlanParser()
        plan = {
            "node_type": "Hash Join",
        }
        join_strategy = parser.extract_join_strategy(plan)
        assert join_strategy == "hash_join"

    def test_extract_relation_names(self):
        """Test relation name extraction."""
        parser = PlanParser()
        plan = {
            "node_type": "Seq Scan",
            "relation_name": "users",
            "plans": [
                {
                    "node_type": "Index Scan",
                    "relation_name": "posts",
                },
            ],
        }
        relations = parser.extract_relation_names(plan)
        assert "users" in relations
        assert "posts" in relations

    def test_calculate_total_cost(self):
        """Test total cost calculation."""
        parser = PlanParser()
        plan = {
            "total_cost": 100.0,
            "plans": [
                {"total_cost": 50.0},
                {"total_cost": 50.0},
            ],
        }
        total_cost = parser.calculate_total_cost(plan)
        assert total_cost == 100.0

    def test_get_plan_depth(self):
        """Test plan depth calculation."""
        parser = PlanParser()
        plan = {
            "node_type": "Hash Join",
            "plans": [
                {
                    "node_type": "Seq Scan",
                    "plans": [
                        {"node_type": "Index Scan"},
                    ],
                },
                {
                    "node_type": "Index Scan",
                },
            ],
        }
        depth = parser.get_plan_depth(plan)
        assert depth == 3

    def test_get_node_count(self):
        """Test node count calculation."""
        parser = PlanParser()
        plan = {
            "node_type": "Hash Join",
            "plans": [
                {"node_type": "Seq Scan"},
                {"node_type": "Index Scan"},
            ],
        }
        count = parser.get_node_count(plan)
        assert count == 3

    def test_get_scan_types(self):
        """Test scan types extraction."""
        parser = PlanParser()
        plan = {
            "node_type": "Hash Join",
            "plans": [
                {"node_type": "Seq Scan"},
                {"node_type": "Index Scan"},
            ],
        }
        scan_types = parser.get_scan_types(plan)
        assert "sequential_scan" in scan_types
        assert "index_scan" in scan_types

    def test_generate_plan_hash(self):
        """Test plan hash generation."""
        parser = PlanParser()
        plan = {
            "node_type": "Plan",
            "relation_name": "users",
        }
        hash1 = parser.generate_plan_hash(plan)
        hash2 = parser.generate_plan_hash(plan)
        assert hash1 == hash2


class TestMetricExtractor:
    """Tests for MetricExtractor."""

    def test_extract_metrics(self):
        """Test metric extraction."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Seq Scan",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }
        metrics = extractor.extract_metrics(plan_json)
        assert metrics["total_cost"] == 25.50
        assert metrics["plan_rows"] == 1000
        assert metrics["node_type"] == "Seq Scan"

    def test_extract_nested_metrics(self):
        """Test nested metric extraction."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 30.00,
            "Plan Rows": 100,
            "Plan Width": 8,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                },
                {
                    "Node Type": "Index Scan",
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                },
            ],
        }
        metrics = extractor.extract_nested_metrics(plan_json)
        assert metrics["total_cost"] == 30.00
        assert "nested_plans" in metrics
        assert len(metrics["nested_plans"]) == 2

    def test_detect_expensive_nodes(self):
        """Test expensive node detection."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Seq Scan",
            "Total Cost": 1500.0,
            "Plan Rows": 100000,
        }
        expensive = extractor.detect_expensive_nodes(plan_json, cost_threshold=1000.0)
        assert len(expensive) == 1
        assert expensive[0]["cost"] == 1500.0

    def test_detect_sequential_scans(self):
        """Test sequential scan detection."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
        }
        scans = extractor.detect_sequential_scans(plan_json)
        assert len(scans) == 1
        assert scans[0]["relation_name"] == "users"

    def test_detect_missing_indexes(self):
        """Test missing index detection."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Plan Rows": 100000,
        }
        missing = extractor.detect_missing_indexes(plan_json)
        assert len(missing) == 1
        assert missing[0]["relation_name"] == "users"

    def test_get_cost_breakdown(self):
        """Test cost breakdown."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Hash Join",
            "Total Cost": 30.00,
            "Plans": [
                {"Node Type": "Seq Scan", "Total Cost": 15.00},
                {"Node Type": "Index Scan", "Total Cost": 14.00},
            ],
        }
        breakdown = extractor.get_cost_breakdown(plan_json)
        assert len(breakdown) == 3

    def test_get_scan_type_distribution(self):
        """Test scan type distribution."""
        extractor = MetricExtractor()
        plan_json = {
            "Node Type": "Hash Join",
            "Plans": [
                {"Node Type": "Seq Scan"},
                {"Node Type": "Index Scan"},
            ],
        }
        distribution = extractor.get_scan_type_distribution(plan_json)
        assert distribution["sequential_scan"] == 1
        assert distribution["index_scan"] == 1
