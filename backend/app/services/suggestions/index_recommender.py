"""Index recommender module for suggesting database indexes."""
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from app.core.logging import get_logger
from app.models.diagnostic import Diagnostic
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.query import ExtractedQuery

logger = get_logger(__name__)


@dataclass
class IndexRecommendation:
    """Represents an index recommendation."""

    table_name: str
    column_names: list[str]
    index_type: str  # btree, hash, gin, gist
    recommendation_type: str  # single_column, composite, partial
    selectivity_estimate: float
    confidence_score: float
    impact_estimate: str  # high, medium, low
    reason: str
    sql_statement: str
    related_query_ids: list[int]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "column_names": self.column_names,
            "index_type": self.index_type,
            "recommendation_type": self.recommendation_type,
            "selectivity_estimate": self.selectivity_estimate,
            "confidence_score": self.confidence_score,
            "impact_estimate": self.impact_estimate,
            "reason": self.reason,
            "sql_statement": self.sql_statement,
            "related_query_ids": self.related_query_ids,
        }


class IndexRecommender:
    """Recommends database indexes based on query analysis."""

    def __init__(self) -> None:
        """Initialize index recommender."""
        pass

    def analyze_query_for_indexes(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel | None,
    ) -> list[IndexRecommendation]:
        """
        Analyze a query for index recommendations.

        Args:
            query: Extracted query
            plan: Execution plan

        Returns:
            List of index recommendations
        """
        recommendations = []

        if not plan:
            return recommendations

        # Analyze execution plan for sequential scans
        seq_scan_recommendations = self._analyze_sequential_scans(query, plan)
        recommendations.extend(seq_scan_recommendations)

        # Analyze WHERE clauses for index opportunities
        where_recommendations = self._analyze_where_clauses(query)
        recommendations.extend(where_recommendations)

        # Analyze JOIN clauses for index opportunities
        join_recommendations = self._analyze_join_clauses(query)
        recommendations.extend(join_recommendations)

        # Analyze ORDER BY for index opportunities
        order_recommendations = self._analyze_order_by(query)
        recommendations.extend(order_recommendations)

        return recommendations

    def _analyze_sequential_scans(
        self,
        query: ExtractedQuery,
        plan: ExecutionPlanModel,
    ) -> list[IndexRecommendation]:
        """Analyze sequential scans for index opportunities."""
        recommendations = []

        def find_seq_scans(node: dict[str, Any], path: list[str] = []) -> None:
            """Recursively find sequential scans."""
            node_type = node.get("Node Type", "")

            if node_type == "Seq Scan":
                relation_name = node.get("Relation Name", "")
                alias = node.get("Alias", relation_name)

                # Extract columns from filter conditions
                filter_condition = node.get("Filter", "")
                if filter_condition:
                    columns = self._extract_columns_from_condition(filter_condition)

                    for column in columns:
                        recommendation = IndexRecommendation(
                            table_name=relation_name,
                            column_names=[column],
                            index_type="btree",
                            recommendation_type="single_column",
                            selectivity_estimate=0.5,
                            confidence_score=0.8,
                            impact_estimate="high",
                            reason=f"Sequential scan on {relation_name} with filter on {column}",
                            sql_statement=f"CREATE INDEX idx_{relation_name}_{column} ON {relation_name} ({column});",
                            related_query_ids=[query.id],
                        )
                        recommendations.append(recommendation)

            if "Plans" in node:
                for child in node["Plans"]:
                    find_seq_scans(child, path + [node_type])

        find_seq_scans(plan.plan_json)

        return recommendations

    def _analyze_where_clauses(self, query: ExtractedQuery) -> list[IndexRecommendation]:
        """Analyze WHERE clauses for index opportunities."""
        recommendations = []

        # Extract WHERE clause from normalized SQL
        where_match = re.search(r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s+OFFSET|$)", query.normalized_sql, re.IGNORECASE)

        if not where_match:
            return recommendations

        where_clause = where_match.group(1)

        # Extract table and column pairs
        table_columns = self._extract_table_columns_from_where(where_clause)

        for table, columns in table_columns.items():
            for column in columns:
                recommendation = IndexRecommendation(
                    table_name=table,
                    column_names=[column],
                    index_type="btree",
                    recommendation_type="single_column",
                    selectivity_estimate=0.5,
                    confidence_score=0.7,
                    impact_estimate="medium",
                    reason=f"WHERE clause uses {table}.{column} for filtering",
                    sql_statement=f"CREATE INDEX idx_{table}_{column} ON {table} ({column});",
                    related_query_ids=[query.id],
                )
                recommendations.append(recommendation)

        return recommendations

    def _analyze_join_clauses(self, query: ExtractedQuery) -> list[IndexRecommendation]:
        """Analyze JOIN clauses for index opportunities."""
        recommendations = []

        # Find JOIN conditions
        join_pattern = r"JOIN\s+(\w+)\s+(?:AS\s+)?(\w+)\s+ON\s+(.+?)(?:\s+JOIN|\s+WHERE|$)"
        join_matches = re.finditer(join_pattern, query.normalized_sql, re.IGNORECASE)

        for match in join_matches:
            table_name = match.group(1)
            join_condition = match.group(3)

            # Extract columns from join condition
            columns = self._extract_columns_from_condition(join_condition)

            for column in columns:
                recommendation = IndexRecommendation(
                    table_name=table_name,
                    column_names=[column],
                    index_type="btree",
                    recommendation_type="single_column",
                    selectivity_estimate=0.5,
                    confidence_score=0.9,
                    impact_estimate="high",
                    reason=f"JOIN condition uses {table_name}.{column}",
                    sql_statement=f"CREATE INDEX idx_{table_name}_{column} ON {table_name} ({column});",
                    related_query_ids=[query.id],
                )
                recommendations.append(recommendation)

        return recommendations

    def _analyze_order_by(self, query: ExtractedQuery) -> list[IndexRecommendation]:
        """Analyze ORDER BY clauses for index opportunities."""
        recommendations = []

        # Find ORDER BY clause
        order_match = re.search(r"ORDER\s+BY\s+(.+?)(?:\s+LIMIT|\s+OFFSET|$)", query.normalized_sql, re.IGNORECASE)

        if not order_match:
            return recommendations

        order_clause = order_match.group(1)

        # Extract table and column pairs
        table_columns = self._extract_table_columns_from_order(order_clause)

        for table, columns in table_columns.items():
            for column in columns:
                recommendation = IndexRecommendation(
                    table_name=table,
                    column_names=[column],
                    index_type="btree",
                    recommendation_type="single_column",
                    selectivity_estimate=0.5,
                    confidence_score=0.6,
                    impact_estimate="medium",
                    reason=f"ORDER BY uses {table}.{column} for sorting",
                    sql_statement=f"CREATE INDEX idx_{table}_{column} ON {table} ({column});",
                    related_query_ids=[query.id],
                )
                recommendations.append(recommendation)

        return recommendations

    def _extract_columns_from_condition(self, condition: str) -> list[str]:
        """Extract column names from a condition."""
        columns = []

        # Match column references (table.column or just column)
        column_pattern = r"(\w+)\.(\w+)|(\w+)"
        matches = re.findall(column_pattern, condition)

        for match in matches:
            if match[0] and match[1]:  # table.column format
                columns.append(match[1])
            elif match[2]:  # just column
                columns.append(match[2])

        return list(set(columns))

    def _extract_table_columns_from_where(self, where_clause: str) -> dict[str, list[str]]:
        """Extract table and column pairs from WHERE clause."""
        table_columns = defaultdict(list)

        # Match table.column patterns
        pattern = r"(\w+)\.(\w+)"
        matches = re.findall(pattern, where_clause)

        for table, column in matches:
            table_columns[table].append(column)

        # Remove duplicates
        for table in table_columns:
            table_columns[table] = list(set(table_columns[table]))

        return dict(table_columns)

    def _extract_table_columns_from_order(self, order_clause: str) -> dict[str, list[str]]:
        """Extract table and column pairs from ORDER BY clause."""
        table_columns = defaultdict(list)

        # Match table.column patterns
        pattern = r"(\w+)\.(\w+)"
        matches = re.findall(pattern, order_clause)

        for table, column in matches:
            table_columns[table].append(column)

        # Remove duplicates
        for table in table_columns:
            table_columns[table] = list(set(table_columns[table]))

        return dict(table_columns)

    def generate_composite_index_recommendation(
        self,
        table_name: str,
        columns: list[str],
        query_ids: list[int],
    ) -> IndexRecommendation:
        """
        Generate a composite index recommendation.

        Args:
            table_name: Table name
            columns: Column names for composite index
            query_ids: Related query IDs

        Returns:
            Index recommendation
        """
        column_str = ", ".join(columns)

        return IndexRecommendation(
            table_name=table_name,
            column_names=columns,
            index_type="btree",
            recommendation_type="composite",
            selectivity_estimate=0.5,
            confidence_score=0.85,
            impact_estimate="high",
            reason=f"Composite index on {table_name} for multi-column filtering/sorting",
            sql_statement=f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name} ({column_str});",
            related_query_ids=query_ids,
        )

    def generate_partial_index_recommendation(
        self,
        table_name: str,
        column: str,
        condition: str,
        query_ids: list[int],
    ) -> IndexRecommendation:
        """
        Generate a partial index recommendation.

        Args:
            table_name: Table name
            column: Column name
            condition: Partial index condition
            query_ids: Related query IDs

        Returns:
            Index recommendation
        """
        return IndexRecommendation(
            table_name=table_name,
            column_names=[column],
            index_type="btree",
            recommendation_type="partial",
            selectivity_estimate=0.5,
            confidence_score=0.75,
            impact_estimate="medium",
            reason=f"Partial index on {table_name}.{column} with condition: {condition}",
            sql_statement=f"CREATE INDEX idx_{table_name}_{column}_partial ON {table_name} ({column}) WHERE {condition};",
            related_query_ids=query_ids,
        )

    def generate_gin_index_recommendation(
        self,
        table_name: str,
        column: str,
        query_ids: list[int],
    ) -> IndexRecommendation:
        """
        Generate a GIN index recommendation for array/jsonb columns.

        Args:
            table_name: Table name
            column: Column name
            query_ids: Related query IDs

        Returns:
            Index recommendation
        """
        return IndexRecommendation(
            table_name=table_name,
            column_names=[column],
            index_type="gin",
            recommendation_type="single_column",
            selectivity_estimate=0.5,
            confidence_score=0.8,
            impact_estimate="high",
            reason=f"GIN index on {table_name}.{column} for array/jsonb operations",
            sql_statement=f"CREATE INDEX idx_{table_name}_{column}_gin ON {table_name} USING GIN ({column});",
            related_query_ids=query_ids,
        )
