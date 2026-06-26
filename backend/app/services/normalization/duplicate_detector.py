"""Duplicate pattern detection service."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.query import ExtractedQuery
from app.services.normalization.ast_normalizer import ASTNormalizer
from app.services.normalization.sql_parser import SQLParser
from app.services.normalization.structural_comparison import StructuralComparison

logger = get_logger(__name__)


class DuplicateDetector:
    """Service for detecting duplicate query patterns."""

    def __init__(self, dialect: str = "postgres") -> None:
        """
        Initialize duplicate detector.

        Args:
            dialect: SQL dialect to use
        """
        self.parser = SQLParser(dialect)
        self.normalizer = ASTNormalizer(dialect)
        self.comparator = StructuralComparison(dialect)

    def find_exact_duplicates(
        self,
        db: Session,
        codebase_id: int,
    ) -> list[dict[str, Any]]:
        """
        Find exact duplicate queries.

        Args:
            db: Database session
            codebase_id: Codebase ID

        Returns:
            List of duplicate groups
        """
        # Group by query hash
        from sqlalchemy import func

        duplicates = (
            db.query(
                ExtractedQuery.query_hash,
                func.count(ExtractedQuery.id).label("count"),
                func.array_agg(ExtractedQuery.id).label("query_ids"),
            )
            .filter(ExtractedQuery.codebase_id == codebase_id)
            .group_by(ExtractedQuery.query_hash)
            .having(func.count(ExtractedQuery.id) > 1)
            .all()
        )

        results = []
        for duplicate in duplicates:
            # Get query details
            query = (
                db.query(ExtractedQuery)
                .filter(ExtractedQuery.query_hash == duplicate.query_hash)
                .first()
            )

            if query:
                results.append({
                    "query_hash": duplicate.query_hash,
                    "count": duplicate.count,
                    "query_ids": duplicate.query_ids,
                    "normalized_sql": query.normalized_sql,
                    "raw_sql": query.raw_sql,
                })

        return results

    def find_near_duplicates(
        self,
        db: Session,
        codebase_id: int,
        threshold: float = 0.85,
    ) -> list[dict[str, Any]]:
        """
        Find near-duplicate queries based on structural similarity.

        Args:
            db: Database session
            codebase_id: Codebase ID
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of near-duplicate groups
        """
        # Get all queries
        queries = (
            db.query(ExtractedQuery)
            .filter(ExtractedQuery.codebase_id == codebase_id)
            .all()
        )

        # Compare all pairs
        groups = []
        processed = set()

        for i, query1 in enumerate(queries):
            if query1.id in processed:
                continue

            similar_queries = [query1.id]
            canonical1 = self.normalizer.canonical_form(query1.normalized_sql)

            for j, query2 in enumerate(queries[i + 1 :], start=i + 1):
                if query2.id in processed:
                    continue

                canonical2 = self.normalizer.canonical_form(query2.normalized_sql)

                # Compare canonical forms
                if canonical1 == canonical2:
                    similar_queries.append(query2.id)
                    processed.add(query2.id)

            if len(similar_queries) > 1:
                groups.append({
                    "query_ids": similar_queries,
                    "count": len(similar_queries),
                    "canonical_sql": canonical1,
                })

                # Mark all as processed
                for query_id in similar_queries:
                    processed.add(query_id)

        return groups

    def find_structural_duplicates(
        self,
        db: Session,
        codebase_id: int,
        threshold: float = 0.85,
    ) -> list[dict[str, Any]]:
        """
        Find structurally similar queries.

        Args:
            db: Database session
            codebase_id: Codebase ID
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of structural duplicate groups
        """
        # Get all queries
        queries = (
            db.query(ExtractedQuery)
            .filter(ExtractedQuery.codebase_id == codebase_id)
            .all()
        )

        # Compare all pairs using structural comparison
        groups = []
        processed = set()

        for i, query1 in enumerate(queries):
            if query1.id in processed:
                continue

            similar_queries = [(query1.id, 1.0)]
            sig1 = self.normalizer.get_structural_signature(query1.normalized_sql)

            for j, query2 in enumerate(queries[i + 1 :], start=i + 1):
                if query2.id in processed:
                    continue

                sig2 = self.normalizer.get_structural_signature(query2.normalized_sql)

                # Calculate similarity
                similarity = self.comparator._calculate_similarity(sig1, sig2)

                if similarity >= threshold:
                    similar_queries.append((query2.id, similarity))
                    processed.add(query2.id)

            if len(similar_queries) > 1:
                # Sort by similarity
                similar_queries.sort(key=lambda x: x[1], reverse=True)

                groups.append({
                    "query_ids": [q[0] for q in similar_queries],
                    "similarities": [q[1] for q in similar_queries],
                    "count": len(similar_queries),
                    "signature": sig1,
                })

                # Mark all as processed
                for query_id, _ in similar_queries:
                    processed.add(query_id)

        return groups

    def detect_patterns(
        self,
        db: Session,
        codebase_id: int,
    ) -> list[dict[str, Any]]:
        """
        Detect common query patterns.

        Args:
            db: Database session
            codebase_id: Codebase ID

        Returns:
            List of detected patterns
        """
        # Get all queries
        queries = (
            db.query(ExtractedQuery)
            .filter(ExtractedQuery.codebase_id == codebase_id)
            .all()
        )

        # Extract signatures
        signatures = {}
        for query in queries:
            sig = self.normalizer.get_structural_signature(query.normalized_sql)
            if sig not in signatures:
                signatures[sig] = []
            signatures[sig].append(query.id)

        # Find patterns (signatures with multiple queries)
        patterns = []
        for sig, query_ids in signatures.items():
            if len(query_ids) > 1:
                # Get representative query
                query = (
                    db.query(ExtractedQuery)
                    .filter(ExtractedQuery.id == query_ids[0])
                    .first()
                )

                patterns.append({
                    "signature": sig,
                    "count": len(query_ids),
                    "query_ids": query_ids,
                    "representative_sql": query.normalized_sql if query else None,
                })

        # Sort by count (most common first)
        patterns.sort(key=lambda x: x["count"], reverse=True)

        return patterns

    def get_duplicate_statistics(
        self,
        db: Session,
        codebase_id: int,
    ) -> dict[str, Any]:
        """
        Get duplicate detection statistics.

        Args:
            db: Database session
            codebase_id: Codebase ID

        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func

        # Total queries
        total_queries = (
            db.query(func.count(ExtractedQuery.id))
            .filter(ExtractedQuery.codebase_id == codebase_id)
            .scalar()
        )

        # Exact duplicates
        exact_duplicates = self.find_exact_duplicates(db, codebase_id)
        exact_duplicate_count = sum(g["count"] for g in exact_duplicates)
        exact_duplicate_queries = sum(g["count"] - 1 for g in exact_duplicates)

        # Near duplicates
        near_duplicates = self.find_near_duplicates(db, codebase_id)
        near_duplicate_count = sum(g["count"] for g in near_duplicates)
        near_duplicate_queries = sum(g["count"] - 1 for g in near_duplicates)

        # Structural duplicates
        structural_duplicates = self.find_structural_duplicates(db, codebase_id)
        structural_duplicate_count = sum(g["count"] for g in structural_duplicates)
        structural_duplicate_queries = sum(g["count"] - 1 for g in structural_duplicates)

        # Patterns
        patterns = self.detect_patterns(db, codebase_id)

        return {
            "total_queries": total_queries,
            "exact_duplicate_groups": len(exact_duplicates),
            "exact_duplicate_queries": exact_duplicate_queries,
            "near_duplicate_groups": len(near_duplicates),
            "near_duplicate_queries": near_duplicate_queries,
            "structural_duplicate_groups": len(structural_duplicates),
            "structural_duplicate_queries": structural_duplicate_queries,
            "pattern_count": len(patterns),
            "top_patterns": patterns[:10],
        }
