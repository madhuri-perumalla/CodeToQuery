"""Execution plan parser for PostgreSQL EXPLAIN JSON output."""
from dataclasses import dataclass, field
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PlanNode:
    """Base class for plan nodes."""
    node_type: str
    startup_cost: float
    total_cost: float
    plan_rows: float
    plan_width: int
    actual_startup_time: float | None = None
    actual_total_time: float | None = None
    actual_rows: float | None = None
    actual_loops: float | None = None
    parent: "PlanNode | None" = None
    children: list["PlanNode"] = field(default_factory=list)
    path: str = ""
    depth: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "node_type": self.node_type,
            "startup_cost": self.startup_cost,
            "total_cost": self.total_cost,
            "plan_rows": self.plan_rows,
            "plan_width": self.plan_width,
            "actual_startup_time": self.actual_startup_time,
            "actual_total_time": self.actual_total_time,
            "actual_rows": self.actual_rows,
            "actual_loops": self.actual_loops,
            "path": self.path,
            "depth": self.depth,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class SequentialScanNode(PlanNode):
    """Sequential scan node."""
    relation_name: str | None = None
    alias: str | None = None
    schema: str | None = None
    filter: str | None = None
    scan_direction: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "relation_name": self.relation_name,
            "alias": self.alias,
            "schema": self.schema,
            "filter": self.filter,
            "scan_direction": self.scan_direction,
        })
        return base_dict


@dataclass
class IndexScanNode(PlanNode):
    """Index scan node."""
    relation_name: str | None = None
    alias: str | None = None
    schema: str | None = None
    index_name: str | None = None
    index_cond: str | None = None
    filter: str | None = None
    scan_direction: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "relation_name": self.relation_name,
            "alias": self.alias,
            "schema": self.schema,
            "index_name": self.index_name,
            "index_cond": self.index_cond,
            "filter": self.filter,
            "scan_direction": self.scan_direction,
        })
        return base_dict


@dataclass
class BitmapScanNode(PlanNode):
    """Bitmap scan node."""
    relation_name: str | None = None
    alias: str | None = None
    schema: str | None = None
    bitmap_scan_type: str | None = None  # Bitmap Index Scan or Bitmap Heap Scan
    filter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "relation_name": self.relation_name,
            "alias": self.alias,
            "schema": self.schema,
            "bitmap_scan_type": self.bitmap_scan_type,
            "filter": self.filter,
        })
        return base_dict


@dataclass
class NestedLoopNode(PlanNode):
    """Nested loop join node."""
    join_type: str = "Nested Loop"
    parent_relationship: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "join_type": self.join_type,
            "parent_relationship": self.parent_relationship,
        })
        return base_dict


@dataclass
class HashJoinNode(PlanNode):
    """Hash join node."""
    join_type: str = "Hash Join"
    hash_cond: str | None = None
    hash_join_cond: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "join_type": self.join_type,
            "hash_cond": self.hash_cond,
            "hash_join_cond": self.hash_join_cond,
        })
        return base_dict


@dataclass
class MergeJoinNode(PlanNode):
    """Merge join node."""
    join_type: str = "Merge Join"
    merge_cond: str | None = None
    sort_key: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "join_type": self.join_type,
            "merge_cond": self.merge_cond,
            "sort_key": self.sort_key,
        })
        return base_dict


@dataclass
class SortNode(PlanNode):
    """Sort node."""
    sort_key: list[str] | None = None
    sort_key_count: int | None = None
    sort_method: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "sort_key": self.sort_key,
            "sort_key_count": self.sort_key_count,
            "sort_method": self.sort_method,
        })
        return base_dict


@dataclass
class AggregateNode(PlanNode):
    """Aggregate node."""
    strategy: str | None = None  # Plain, Hashed, Sorted
    group_key: list[str] | None = None
    filter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "strategy": self.strategy,
            "group_key": self.group_key,
            "filter": self.filter,
        })
        return base_dict


@dataclass
class ExecutionPlan:
    """Complete execution plan tree."""
    root_node: PlanNode
    total_cost: float
    total_rows: float
    plan_depth: int
    node_count: int
    scan_types: list[str] = field(default_factory=list)
    join_types: list[str] = field(default_factory=list)
    relation_names: list[str] = field(default_factory=list)
    index_names: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "root_node": self.root_node.to_dict(),
            "total_cost": self.total_cost,
            "total_rows": self.total_rows,
            "plan_depth": self.plan_depth,
            "node_count": self.node_count,
            "scan_types": self.scan_types,
            "join_types": self.join_types,
            "relation_names": self.relation_names,
            "index_names": self.index_names,
        }


class ExecutionPlanParser:
    """Parser for PostgreSQL EXPLAIN JSON execution plans."""

    def __init__(self) -> None:
        """Initialize execution plan parser."""
        self.node_count = 0
        self.max_depth = 0
        self.scan_types: set[str] = set()
        self.join_types: set[str] = set()
        self.relation_names: set[str] = set()
        self.index_names: set[str] = set()

    def parse(self, plan_json: dict[str, Any]) -> ExecutionPlan:
        """
        Parse EXPLAIN JSON into structured execution plan.

        Args:
            plan_json: EXPLAIN JSON output

        Returns:
            Structured execution plan
        """
        # Reset counters
        self.node_count = 0
        self.max_depth = 0
        self.scan_types = set()
        self.join_types = set()
        self.relation_names = set()
        self.index_names = set()

        # Parse root node
        root_node = self._parse_node(plan_json, parent=None, path="0", depth=0)

        # Calculate total cost and rows
        total_cost = self._calculate_total_cost(plan_json)
        total_rows = self._calculate_total_rows(plan_json)

        # Create execution plan
        execution_plan = ExecutionPlan(
            root_node=root_node,
            total_cost=total_cost,
            total_rows=total_rows,
            plan_depth=self.max_depth,
            node_count=self.node_count,
            scan_types=list(self.scan_types),
            join_types=list(self.join_types),
            relation_names=list(self.relation_names),
            index_names=list(self.index_names),
        )

        return execution_plan

    def _parse_node(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> PlanNode:
        """
        Parse a single node from JSON.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Parsed plan node
        """
        node_type = node_json.get("Node Type", "")
        self.node_count += 1
        self.max_depth = max(self.max_depth, depth)

        # Create appropriate node type
        if node_type == "Seq Scan":
            node = self._parse_sequential_scan(node_json, parent, path, depth)
        elif node_type == "Index Scan" or node_type == "Index Only Scan":
            node = self._parse_index_scan(node_json, parent, path, depth)
        elif node_type == "Bitmap Index Scan" or node_type == "Bitmap Heap Scan":
            node = self._parse_bitmap_scan(node_json, parent, path, depth)
        elif node_type == "Nested Loop":
            node = self._parse_nested_loop(node_json, parent, path, depth)
        elif node_type == "Hash Join" or node_type.startswith("Hash"):
            node = self._parse_hash_join(node_json, parent, path, depth)
        elif node_type == "Merge Join" or node_type.startswith("Merge"):
            node = self._parse_merge_join(node_json, parent, path, depth)
        elif node_type == "Sort":
            node = self._parse_sort(node_json, parent, path, depth)
        elif node_type == "Aggregate" or node_type == "HashAggregate":
            node = self._parse_aggregate(node_json, parent, path, depth)
        else:
            node = self._parse_generic_node(node_json, parent, path, depth)

        # Parse children recursively
        if "Plans" in node_json:
            for i, child_json in enumerate(node_json["Plans"]):
                child_path = f"{path}.{i}"
                child_node = self._parse_node(child_json, node, child_path, depth + 1)
                node.children.append(child_node)

        return node

    def _parse_generic_node(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> PlanNode:
        """
        Parse a generic node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Generic plan node
        """
        node = PlanNode(
            node_type=node_json.get("Node Type", ""),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
        )

        # Track relation name if present
        if node_json.get("Relation Name"):
            self.relation_names.add(node_json["Relation Name"])

        return node

    def _parse_sequential_scan(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> SequentialScanNode:
        """
        Parse sequential scan node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Sequential scan node
        """
        self.scan_types.add("sequential_scan")
        
        if node_json.get("Relation Name"):
            self.relation_names.add(node_json["Relation Name"])

        node = SequentialScanNode(
            node_type="Seq Scan",
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            relation_name=node_json.get("Relation Name"),
            alias=node_json.get("Alias"),
            schema=node_json.get("Schema"),
            filter=node_json.get("Filter"),
            scan_direction=node_json.get("Scan Direction"),
        )

        return node

    def _parse_index_scan(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> IndexScanNode:
        """
        Parse index scan node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Index scan node
        """
        self.scan_types.add("index_scan")
        
        if node_json.get("Relation Name"):
            self.relation_names.add(node_json["Relation Name"])
        
        if node_json.get("Index Name"):
            self.index_names.add(node_json["Index Name"])

        node = IndexScanNode(
            node_type=node_json.get("Node Type", "Index Scan"),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            relation_name=node_json.get("Relation Name"),
            alias=node_json.get("Alias"),
            schema=node_json.get("Schema"),
            index_name=node_json.get("Index Name"),
            index_cond=node_json.get("Index Cond"),
            filter=node_json.get("Filter"),
            scan_direction=node_json.get("Scan Direction"),
        )

        return node

    def _parse_bitmap_scan(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> BitmapScanNode:
        """
        Parse bitmap scan node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Bitmap scan node
        """
        self.scan_types.add("bitmap_scan")
        
        if node_json.get("Relation Name"):
            self.relation_names.add(node_json["Relation Name"])

        node = BitmapScanNode(
            node_type=node_json.get("Node Type", "Bitmap Scan"),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            relation_name=node_json.get("Relation Name"),
            alias=node_json.get("Alias"),
            schema=node_json.get("Schema"),
            bitmap_scan_type=node_json.get("Node Type"),
            filter=node_json.get("Filter"),
        )

        return node

    def _parse_nested_loop(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> NestedLoopNode:
        """
        Parse nested loop join node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Nested loop node
        """
        self.join_types.add("nested_loop")

        node = NestedLoopNode(
            node_type="Nested Loop",
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            join_type="Nested Loop",
            parent_relationship=node_json.get("Parent Relationship"),
        )

        return node

    def _parse_hash_join(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> HashJoinNode:
        """
        Parse hash join node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Hash join node
        """
        self.join_types.add("hash_join")

        node = HashJoinNode(
            node_type=node_json.get("Node Type", "Hash Join"),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            join_type=node_json.get("Node Type", "Hash Join"),
            hash_cond=node_json.get("Hash Cond"),
            hash_join_cond=node_json.get("Hash Join Cond"),
        )

        return node

    def _parse_merge_join(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> MergeJoinNode:
        """
        Parse merge join node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Merge join node
        """
        self.join_types.add("merge_join")

        node = MergeJoinNode(
            node_type=node_json.get("Node Type", "Merge Join"),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            join_type=node_json.get("Node Type", "Merge Join"),
            merge_cond=node_json.get("Merge Cond"),
            sort_key=node_json.get("Sort Key"),
        )

        return node

    def _parse_sort(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> SortNode:
        """
        Parse sort node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Sort node
        """
        node = SortNode(
            node_type="Sort",
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            sort_key=node_json.get("Sort Key"),
            sort_key_count=node_json.get("Sort Key Count"),
            sort_method=node_json.get("Sort Method"),
        )

        return node

    def _parse_aggregate(
        self,
        node_json: dict[str, Any],
        parent: PlanNode | None,
        path: str,
        depth: int,
    ) -> AggregateNode:
        """
        Parse aggregate node.

        Args:
            node_json: Node JSON
            parent: Parent node
            path: Node path
            depth: Current depth

        Returns:
            Aggregate node
        """
        node = AggregateNode(
            node_type=node_json.get("Node Type", "Aggregate"),
            startup_cost=node_json.get("Startup Cost", 0.0),
            total_cost=node_json.get("Total Cost", 0.0),
            plan_rows=node_json.get("Plan Rows", 0.0),
            plan_width=node_json.get("Plan Width", 0),
            actual_startup_time=node_json.get("Actual Startup Time"),
            actual_total_time=node_json.get("Actual Total Time"),
            actual_rows=node_json.get("Actual Rows"),
            actual_loops=node_json.get("Actual Loops"),
            parent=parent,
            path=path,
            depth=depth,
            strategy=node_json.get("Strategy"),
            group_key=node_json.get("Group Key"),
            filter=node_json.get("Filter"),
        )

        return node

    def _calculate_total_cost(self, plan_json: dict[str, Any]) -> float:
        """
        Calculate total cost from plan.

        Args:
            plan_json: Plan JSON

        Returns:
            Total cost
        """
        return plan_json.get("Total Cost", 0.0)

    def _calculate_total_rows(self, plan_json: dict[str, Any]) -> float:
        """
        Calculate total rows from plan.

        Args:
            plan_json: Plan JSON

        Returns:
            Total rows
        """
        return plan_json.get("Plan Rows", 0.0)

    def find_nodes_by_type(
        self,
        execution_plan: ExecutionPlan,
        node_type: str,
    ) -> list[PlanNode]:
        """
        Find all nodes of a specific type.

        Args:
            execution_plan: Execution plan
            node_type: Node type to find

        Returns:
            List of matching nodes
        """
        matching_nodes = []

        def find_recursive(node: PlanNode):
            if node.node_type == node_type:
                matching_nodes.append(node)
            for child in node.children:
                find_recursive(child)

        find_recursive(execution_plan.root_node)
        return matching_nodes

    def find_nodes_by_cost(
        self,
        execution_plan: ExecutionPlan,
        min_cost: float,
        max_cost: float | None = None,
    ) -> list[PlanNode]:
        """
        Find nodes within a cost range.

        Args:
            execution_plan: Execution plan
            min_cost: Minimum cost
            max_cost: Maximum cost (optional)

        Returns:
            List of matching nodes
        """
        matching_nodes = []

        def find_recursive(node: PlanNode):
            if node.total_cost >= min_cost:
                if max_cost is None or node.total_cost <= max_cost:
                    matching_nodes.append(node)
            for child in node.children:
                find_recursive(child)

        find_recursive(execution_plan.root_node)
        return matching_nodes

    def find_nodes_by_relation(
        self,
        execution_plan: ExecutionPlan,
        relation_name: str,
    ) -> list[PlanNode]:
        """
        Find all nodes for a specific relation.

        Args:
            execution_plan: Execution plan
            relation_name: Relation name

        Returns:
            List of matching nodes
        """
        matching_nodes = []

        def find_recursive(node: PlanNode):
            if isinstance(node, (SequentialScanNode, IndexScanNode, BitmapScanNode)):
                if node.relation_name == relation_name:
                    matching_nodes.append(node)
            for child in node.children:
                find_recursive(child)

        find_recursive(execution_plan.root_node)
        return matching_nodes

    def get_plan_statistics(self, execution_plan: ExecutionPlan) -> dict[str, Any]:
        """
        Get statistics about the execution plan.

        Args:
            execution_plan: Execution plan

        Returns:
            Plan statistics
        """
        scan_nodes = self.find_nodes_by_type(execution_plan, "Seq Scan")
        index_nodes = self.find_nodes_by_type(execution_plan, "Index Scan")
        join_nodes = self.find_nodes_by_type(execution_plan, "Hash Join")
        join_nodes.extend(self.find_nodes_by_type(execution_plan, "Merge Join"))
        join_nodes.extend(self.find_nodes_by_type(execution_plan, "Nested Loop"))

        return {
            "total_cost": execution_plan.total_cost,
            "total_rows": execution_plan.total_rows,
            "plan_depth": execution_plan.plan_depth,
            "node_count": execution_plan.node_count,
            "sequential_scan_count": len(scan_nodes),
            "index_scan_count": len(index_nodes),
            "join_count": len(join_nodes),
            "scan_types": execution_plan.scan_types,
            "join_types": execution_plan.join_types,
            "relation_names": execution_plan.relation_names,
            "index_names": execution_plan.index_names,
        }
