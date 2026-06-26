"""Grouping service wrapper for analysis pipeline."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.group import QueryGroup, GroupMember
from app.services.grouping.pattern_grouping_service import PatternGroupingService

logger = get_logger(__name__)


class GroupingService:
    """Service for grouping similar queries."""

    def __init__(self) -> None:
        """Initialize grouping service."""
        self.pattern_service = PatternGroupingService()

    def group_queries(
        self,
        db: Session,
        codebase_id: int,
    ) -> dict[str, Any]:
        """
        Group queries by patterns and store in database.

        Args:
            db: Database session
            codebase_id: Codebase ID

        Returns:
            Dictionary with grouping results
        """
        try:
            logger.info(f"Grouping queries for codebase {codebase_id}")

            results = self.pattern_service.analyze_codebase_patterns(
                codebase_id=codebase_id,
                db=db,
            )

            patterns = results.get("patterns", [])
            groups_created = 0

            # Store patterns in database
            for pattern_dict in patterns:
                try:
                    # Check if pattern already exists
                    existing = db.query(QueryGroup).filter(
                        QueryGroup.codebase_id == codebase_id,
                        QueryGroup.pattern_signature == pattern_dict.get("pattern_signature")
                    ).first()

                    if existing:
                        # Update existing group
                        existing.query_count = pattern_dict.get("query_count", existing.query_count)
                        existing.files_impacted = pattern_dict.get("files_impacted", existing.files_impacted)
                        existing.total_cost = pattern_dict.get("total_cost", existing.total_cost)
                        existing.max_cost = pattern_dict.get("max_cost", existing.max_cost)
                        existing.avg_cost = pattern_dict.get("avg_cost", existing.avg_cost)
                        existing.total_rows = pattern_dict.get("total_rows", existing.total_rows)
                        existing.max_rows = pattern_dict.get("max_rows", existing.max_rows)
                        existing.avg_rows = pattern_dict.get("avg_rows", existing.avg_rows)
                        existing.risk_score = pattern_dict.get("risk_score", existing.risk_score)
                        existing.severity = pattern_dict.get("severity", existing.severity)
                        existing.meta_data = pattern_dict.get("metadata", existing.meta_data)
                        db.flush()
                        groups_created += 1
                    else:
                        # Create new group
                        group = QueryGroup(
                            codebase_id=codebase_id,
                            name=f"{pattern_dict.get('pattern_type', 'unknown')}_{pattern_dict.get('pattern_signature', '')[:16]}",
                            pattern_type=pattern_dict.get("pattern_type", "unknown"),
                            pattern_signature=pattern_dict.get("pattern_signature", ""),
                            query_count=pattern_dict.get("query_count", 0),
                            files_impacted=pattern_dict.get("files_impacted", 0),
                            total_cost=pattern_dict.get("total_cost", 0),
                            max_cost=pattern_dict.get("max_cost", 0),
                            avg_cost=pattern_dict.get("avg_cost", 0),
                            total_rows=pattern_dict.get("total_rows", 0),
                            max_rows=pattern_dict.get("max_rows", 0),
                            avg_rows=pattern_dict.get("avg_rows", 0),
                            risk_score=pattern_dict.get("risk_score", 0),
                            severity=pattern_dict.get("severity", "low"),
                            sample_query_id=pattern_dict.get("sample_query_id"),
                            meta_data=pattern_dict.get("metadata", {}),
                        )
                        db.add(group)
                        db.flush()

                        # Add group members
                        query_ids = pattern_dict.get("metadata", {}).get("query_ids", [])
                        for query_id in query_ids:
                            member = GroupMember(
                                group_id=group.id,
                                query_id=query_id,
                                similarity_score=1.0,  # Exact match for pattern groups
                                is_representative=1 if query_id == pattern_dict.get("sample_query_id") else 0,
                            )
                            db.add(member)

                        groups_created += 1

                except Exception as e:
                    logger.error(f"Error storing pattern group: {e}")
                    continue

            db.commit()
            logger.info(f"Stored {groups_created} pattern groups in database for codebase {codebase_id}")

            return {
                "codebase_id": codebase_id,
                "groups_created": groups_created,
                "patterns": patterns,
                "statistics": results.get("statistics", {}),
            }

        except Exception as e:
            logger.error(f"Error grouping queries for codebase {codebase_id}: {e}")
            db.rollback()
            raise
