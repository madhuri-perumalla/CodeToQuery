"""Tests for diagnostic rules."""
import pytest

from app.services.diagnostics import (
    ExpensiveJoinRule,
    FullTableScanRule,
    HighCostRule,
    HighRowEstimateRule,
    MissingIndexRule,
    SequentialScanRule,
    SortCostRule,
)


class TestFullTableScanRule:
    """Tests for FullTableScanRule."""

    def test_detects_full_table_scan(self):
        """Test detection of full table scan with high row count."""
        rule = FullTableScanRule(row_threshold=10000)
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 15000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "full_table_scan"
        assert results[0].severity == "warning"
        assert "15000" in results[0].explanation
        assert results[0].evidence["plan_rows"] == 15000

    def test_ignores_small_table_scan(self):
        """Test that small table scans are ignored."""
        rule = FullTableScanRule(row_threshold=10000)
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 5000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestSequentialScanRule:
    """Tests for SequentialScanRule."""

    def test_detects_sequential_scan(self):
        """Test detection of sequential scan."""
        rule = SequentialScanRule()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "sequential_scan"
        assert "users" in results[0].explanation
        assert results[0].evidence["relation_name"] == "users"

    def test_ignores_index_scan(self):
        """Test that index scans are ignored."""
        rule = SequentialScanRule()
        plan_json = {
            "Node Type": "Index Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 15.50,
            "Plan Rows": 100,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestMissingIndexRule:
    """Tests for MissingIndexRule."""

    def test_detects_missing_index_with_filter(self):
        """Test detection of missing index with filter."""
        rule = MissingIndexRule()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Filter": "(email = 'test@example.com')",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "missing_index"
        assert "filter condition" in results[0].explanation.lower()
        assert results[0].evidence["filter"] == "(email = 'test@example.com')"

    def test_detects_full_table_scan_without_filter(self):
        """Test detection of full table scan without filter."""
        rule = MissingIndexRule()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].severity == "info"
        assert "without any filter" in results[0].explanation.lower()


class TestHighCostRule:
    """Tests for HighCostRule."""

    def test_detects_high_cost(self):
        """Test detection of high cost."""
        rule = HighCostRule(threshold=1000.0)
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 1500.00,
            "Plan Rows": 100,
            "Plan Width": 8,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "high_cost"
        assert "1500" in results[0].explanation
        assert results[0].evidence["total_cost"] == 1500.0

    def test_ignores_low_cost(self):
        """Test that low cost nodes are ignored."""
        rule = HighCostRule(threshold=1000.0)
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 500.00,
            "Plan Rows": 100,
            "Plan Width": 8,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestExpensiveJoinRule:
    """Tests for ExpensiveJoinRule."""

    def test_detects_expensive_hash_join(self):
        """Test detection of expensive hash join."""
        rule = ExpensiveJoinRule(threshold=500.0)
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 600.00,
            "Plan Rows": 100,
            "Plan Width": 8,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "expensive_join"
        assert "Hash Join" in results[0].explanation
        assert results[0].evidence["total_cost"] == 600.0

    def test_detects_expensive_merge_join(self):
        """Test detection of expensive merge join."""
        rule = ExpensiveJoinRule(threshold=500.0)
        plan_json = {
            "Node Type": "Merge Join",
            "Startup Cost": 1.00,
            "Total Cost": 600.00,
            "Plan Rows": 100,
            "Plan Width": 8,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "expensive_join"
        assert "Merge Join" in results[0].explanation

    def test_ignores_cheap_join(self):
        """Test that cheap joins are ignored."""
        rule = ExpensiveJoinRule(threshold=500.0)
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 300.00,
            "Plan Rows": 100,
            "Plan Width": 8,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestHighRowEstimateRule:
    """Tests for HighRowEstimateRule."""

    def test_detects_high_row_estimate(self):
        """Test detection of high row estimate."""
        rule = HighRowEstimateRule(threshold=100000)
        plan_json = {
            "Node Type": "Seq Scan",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 150000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "high_row_estimate"
        assert "150000" in results[0].explanation
        assert results[0].evidence["plan_rows"] == 150000

    def test_ignores_low_row_estimate(self):
        """Test that low row estimates are ignored."""
        rule = HighRowEstimateRule(threshold=100000)
        plan_json = {
            "Node Type": "Seq Scan",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 50000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestSortCostRule:
    """Tests for SortCostRule."""

    def test_detects_high_sort_cost(self):
        """Test detection of high sort cost."""
        rule = SortCostRule(threshold=200.0)
        plan_json = {
            "Node Type": "Sort",
            "Startup Cost": 10.00,
            "Total Cost": 300.00,
            "Plan Rows": 10000,
            "Plan Width": 4,
            "Sort Key": ["created_at"],
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 1
        assert results[0].rule_id == "sort_cost"
        assert "Sort operation" in results[0].explanation
        assert results[0].evidence["total_cost"] == 300.0

    def test_ignores_low_sort_cost(self):
        """Test that low sort costs are ignored."""
        rule = SortCostRule(threshold=200.0)
        plan_json = {
            "Node Type": "Sort",
            "Startup Cost": 10.00,
            "Total Cost": 150.00,
            "Plan Rows": 10000,
            "Plan Width": 4,
            "Sort Key": ["created_at"],
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0

    def test_ignores_non_sort_nodes(self):
        """Test that non-sort nodes are ignored."""
        rule = SortCostRule(threshold=200.0)
        plan_json = {
            "Node Type": "Seq Scan",
            "Startup Cost": 0.00,
            "Total Cost": 300.00,
            "Plan Rows": 10000,
            "Plan Width": 4,
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 0


class TestNestedPlans:
    """Tests for nested plan evaluation."""

    def test_evaluates_nested_plans(self):
        """Test that rules evaluate nested plans."""
        rule = SequentialScanRule()
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
                    "Node Type": "Seq Scan",
                    "Relation Name": "posts",
                    "Startup Cost": 0.00,
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                    "Plan Width": 4,
                },
            ],
        }

        results = rule.evaluate(plan_json)

        assert len(results) == 2
        assert all(r.rule_id == "sequential_scan" for r in results)
