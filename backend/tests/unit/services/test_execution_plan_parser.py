"""Tests for Execution Plan Parser."""
import pytest

from app.services.explain.execution_plan_parser import (
    AggregateNode,
    BitmapScanNode,
    ExecutionPlan,
    ExecutionPlanParser,
    HashJoinNode,
    IndexScanNode,
    MergeJoinNode,
    NestedLoopNode,
    SequentialScanNode,
    SortNode,
)


class TestExecutionPlanParser:
    """Tests for ExecutionPlanParser."""

    def test_parse_simple_sequential_scan(self):
        """Test parsing a simple sequential scan."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, SequentialScanNode)
        assert execution_plan.root_node.node_type == "Seq Scan"
        assert execution_plan.root_node.relation_name == "users"
        assert execution_plan.root_node.total_cost == 25.50
        assert execution_plan.plan_depth == 0
        assert execution_plan.node_count == 1
        assert "sequential_scan" in execution_plan.scan_types
        assert "users" in execution_plan.relation_names

    def test_parse_index_scan(self):
        """Test parsing an index scan."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Index Scan",
            "Relation Name": "users",
            "Index Name": "users_email_idx",
            "Startup Cost": 0.00,
            "Total Cost": 15.50,
            "Plan Rows": 100,
            "Plan Width": 4,
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, IndexScanNode)
        assert execution_plan.root_node.node_type == "Index Scan"
        assert execution_plan.root_node.relation_name == "users"
        assert execution_plan.root_node.index_name == "users_email_idx"
        assert "index_scan" in execution_plan.scan_types
        assert "users_email_idx" in execution_plan.index_names

    def test_parse_nested_plan(self):
        """Test parsing a nested plan with join."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 30.00,
            "Plan Rows": 100,
            "Plan Width": 8,
            "Hash Cond": "(users.id = posts.user_id)",
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
                    "Index Name": "posts_user_id_idx",
                    "Startup Cost": 0.00,
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                    "Plan Width": 4,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, HashJoinNode)
        assert execution_plan.root_node.node_type == "Hash Join"
        assert execution_plan.root_node.hash_cond == "(users.id = posts.user_id)"
        assert len(execution_plan.root_node.children) == 2
        assert isinstance(execution_plan.root_node.children[0], SequentialScanNode)
        assert isinstance(execution_plan.root_node.children[1], IndexScanNode)
        assert execution_plan.plan_depth == 1
        assert execution_plan.node_count == 3

    def test_parse_deeply_nested_plan(self):
        """Test parsing a deeply nested plan."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Startup Cost": 1.00,
            "Total Cost": 50.00,
            "Plan Rows": 100,
            "Plan Width": 8,
            "Plans": [
                {
                    "Node Type": "Nested Loop",
                    "Startup Cost": 0.00,
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
                            "Index Name": "posts_user_id_idx",
                            "Startup Cost": 0.00,
                            "Total Cost": 14.00,
                            "Plan Rows": 100,
                            "Plan Width": 4,
                        },
                    ],
                },
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "comments",
                    "Startup Cost": 0.00,
                    "Total Cost": 19.00,
                    "Plan Rows": 500,
                    "Plan Width": 4,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert execution_plan.plan_depth == 2
        assert execution_plan.node_count == 4
        assert isinstance(execution_plan.root_node, HashJoinNode)
        assert isinstance(execution_plan.root_node.children[0], NestedLoopNode)
        assert isinstance(execution_plan.root_node.children[0].children[0], SequentialScanNode)

    def test_parse_bitmap_scan(self):
        """Test parsing a bitmap scan."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Bitmap Index Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 10.00,
            "Plan Rows": 100,
            "Plan Width": 4,
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, BitmapScanNode)
        assert execution_plan.root_node.bitmap_scan_type == "Bitmap Index Scan"
        assert "bitmap_scan" in execution_plan.scan_types

    def test_parse_merge_join(self):
        """Test parsing a merge join."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Merge Join",
            "Startup Cost": 1.00,
            "Total Cost": 30.00,
            "Plan Rows": 100,
            "Plan Width": 8,
            "Merge Cond": "(users.id = posts.user_id)",
            "Sort Key": ["users.id", "posts.user_id"],
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, MergeJoinNode)
        assert execution_plan.root_node.merge_cond == "(users.id = posts.user_id)"
        assert execution_plan.root_node.sort_key == ["users.id", "posts.user_id"]
        assert "merge_join" in execution_plan.join_types

    def test_parse_sort(self):
        """Test parsing a sort node."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Sort",
            "Startup Cost": 10.00,
            "Total Cost": 15.00,
            "Plan Rows": 1000,
            "Plan Width": 4,
            "Sort Key": ["created_at"],
            "Sort Key Count": 1,
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, SortNode)
        assert execution_plan.root_node.sort_key == ["created_at"]
        assert execution_plan.root_node.sort_key_count == 1

    def test_parse_aggregate(self):
        """Test parsing an aggregate node."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Aggregate",
            "Startup Cost": 15.00,
            "Total Cost": 20.00,
            "Plan Rows": 100,
            "Plan Width": 4,
            "Strategy": "Hashed",
            "Group Key": ["user_id"],
        }
        
        execution_plan = parser.parse(plan_json)
        
        assert isinstance(execution_plan.root_node, AggregateNode)
        assert execution_plan.root_node.strategy == "Hashed"
        assert execution_plan.root_node.group_key == ["user_id"]

    def test_find_nodes_by_type(self):
        """Test finding nodes by type."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "users",
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                },
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "posts",
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        seq_scans = parser.find_nodes_by_type(execution_plan, "Seq Scan")
        
        assert len(seq_scans) == 2
        assert all(isinstance(node, SequentialScanNode) for node in seq_scans)

    def test_find_nodes_by_cost(self):
        """Test finding nodes by cost range."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Total Cost": 30.00,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                },
                {
                    "Node Type": "Seq Scan",
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        expensive_nodes = parser.find_nodes_by_cost(execution_plan, min_cost=14.50)
        
        assert len(expensive_nodes) == 2

    def test_find_nodes_by_relation(self):
        """Test finding nodes by relation name."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "users",
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                },
                {
                    "Node Type": "Index Scan",
                    "Relation Name": "posts",
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        users_nodes = parser.find_nodes_by_relation(execution_plan, "users")
        
        assert len(users_nodes) == 1
        assert users_nodes[0].relation_name == "users"

    def test_get_plan_statistics(self):
        """Test getting plan statistics."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Hash Join",
            "Total Cost": 30.00,
            "Plan Rows": 100,
            "Plans": [
                {
                    "Node Type": "Seq Scan",
                    "Relation Name": "users",
                    "Total Cost": 15.00,
                    "Plan Rows": 1000,
                },
                {
                    "Node Type": "Index Scan",
                    "Relation Name": "posts",
                    "Total Cost": 14.00,
                    "Plan Rows": 100,
                },
            ],
        }
        
        execution_plan = parser.parse(plan_json)
        statistics = parser.get_plan_statistics(execution_plan)
        
        assert statistics["total_cost"] == 30.00
        assert statistics["total_rows"] == 100
        assert statistics["plan_depth"] == 1
        assert statistics["node_count"] == 3
        assert statistics["sequential_scan_count"] == 1
        assert statistics["index_scan_count"] == 1
        assert statistics["join_count"] == 1
        assert "sequential_scan" in statistics["scan_types"]
        assert "hash_join" in statistics["join_types"]
        assert "users" in statistics["relation_names"]
        assert "posts" in statistics["relation_names"]

    def test_node_to_dict(self):
        """Test node to dictionary conversion."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }
        
        execution_plan = parser.parse(plan_json)
        node_dict = execution_plan.root_node.to_dict()
        
        assert node_dict["node_type"] == "Seq Scan"
        assert node_dict["relation_name"] == "users"
        assert node_dict["total_cost"] == 25.50
        assert node_dict["path"] == "0"
        assert node_dict["depth"] == 0
        assert node_dict["children"] == []

    def test_execution_plan_to_dict(self):
        """Test execution plan to dictionary conversion."""
        parser = ExecutionPlanParser()
        plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Startup Cost": 0.00,
            "Total Cost": 25.50,
            "Plan Rows": 1000,
            "Plan Width": 4,
        }
        
        execution_plan = parser.parse(plan_json)
        plan_dict = execution_plan.to_dict()
        
        assert "root_node" in plan_dict
        assert plan_dict["total_cost"] == 25.50
        assert plan_dict["total_rows"] == 1000
        assert plan_dict["plan_depth"] == 0
        assert plan_dict["node_count"] == 1
        assert "scan_types" in plan_dict
        assert "join_types" in plan_dict
        assert "relation_names" in plan_dict
