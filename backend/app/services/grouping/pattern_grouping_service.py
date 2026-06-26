"""Pattern grouping service for query pattern analysis."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.execution_plan import ExecutionPlan as ExecutionPlanModel
from app.models.location import QueryLocation
from app.models.query import ExtractedQuery
from app.services.grouping.duplicate_detector import DuplicateDetector
from app.services.grouping.pattern_detector import PatternDetector
from app.services.grouping.query_pattern import PatternMatch, PatternStatistics, QueryPattern

logger = get_logger(__name__)


class PatternGroupingService:
    """Service for grouping queries by patterns and calculating risk scores."""

    def __init__(self) -> None:
        """Initialize pattern grouping service."""
        self.duplicate_detector = DuplicateDetector()
        self.pattern_detector = PatternDetector()

    def analyze_codebase_patterns(
        self,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Analyze all patterns in a codebase.

        Args:
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Dictionary with patterns and statistics
        """
        # Get all queries in codebase
        queries = db.query(ExtractedQuery).filter(ExtractedQuery.codebase_id == codebase_id).all()

        if not queries:
            return {
                "codebase_id": codebase_id,
                "patterns": [],
                "statistics": self._create_empty_statistics(),
            }

        # Detect all patterns
        all_patterns = []

        # Detect duplicates
        duplicate_patterns = self.duplicate_detector.detect_duplicates_with_cost(queries, db)
        all_patterns.extend(duplicate_patterns)

        # Detect near-duplicates
        near_duplicate_patterns = self.duplicate_detector.detect_near_duplicates_with_cost(queries, db)
        all_patterns.extend(near_duplicate_patterns)

        # Detect common patterns
        pattern_patterns = self.pattern_detector.detect_patterns(queries, db)
        all_patterns.extend(pattern_patterns)

        # Calculate statistics
        statistics = self._calculate_statistics(queries, all_patterns)

        return {
            "codebase_id": codebase_id,
            "total_queries": len(queries),
            "patterns": [p.to_dict() for p in all_patterns],
            "statistics": statistics.to_dict(),
        }

    def get_pattern_inventory(
        self,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Get pattern inventory for a codebase.

        Args:
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Pattern inventory grouped by type
        """
        result = self.analyze_codebase_patterns(codebase_id, db)

        # Group patterns by type
        inventory: dict[str, list[dict[str, Any]]] = {
            "duplicate": [],
            "expensive": [],
            "anti_pattern": [],
            "common": [],
        }

        for pattern in result["patterns"]:
            pattern_type = pattern["pattern_type"]
            if pattern_type in inventory:
                inventory[pattern_type].append(pattern)

        return {
            "codebase_id": codebase_id,
            "inventory": inventory,
            "total_patterns": result["statistics"]["total_patterns"],
        }

    def get_high_risk_patterns(
        self,
        codebase_id: int,
        db: Session,
        risk_threshold: float = 50.0,
    ) -> list[dict[str, Any]]:
        """
        Get high-risk patterns above threshold.

        Args:
            codebase_id: Codebase ID
            db: Database session
            risk_threshold: Minimum risk score

        Returns:
            List of high-risk patterns
        """
        result = self.analyze_codebase_patterns(codebase_id, db)

        high_risk = [p for p in result["patterns"] if p["risk_score"] >= risk_threshold]

        # Sort by risk score descending
        high_risk.sort(key=lambda x: x["risk_score"], reverse=True)

        return high_risk

    def get_pattern_details(
        self,
        pattern_id: str,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Get details for a specific pattern.

        Args:
            pattern_id: Pattern ID
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Pattern details with matching queries
        """
        result = self.analyze_codebase_patterns(codebase_id, db)

        # Find pattern
        pattern = next((p for p in result["patterns"] if p["pattern_id"] == pattern_id), None)

        if not pattern:
            return {
                "error": f"Pattern {pattern_id} not found",
            }

        # Get matching queries
        query_ids = pattern.get("metadata", {}).get("query_ids", [])
        queries = db.query(ExtractedQuery).filter(ExtractedQuery.id.in_(query_ids)).all()

        # Get locations
        locations = db.query(QueryLocation).filter(QueryLocation.query_id.in_(query_ids)).all()

        # Get execution plans
        plans = db.query(ExecutionPlanModel).filter(ExecutionPlanModel.query_id.in_(query_ids)).all()

        # Build matches
        matches = []
        for query_id in query_ids:
            query = next((q for q in queries if q.id == query_id), None)
            if not query:
                continue

            plan = next((p for p in plans if p.query_id == query_id), None)
            loc = next((l for l in locations if l.query_id == query_id), None)

            match = {
                "query_id": query_id,
                "normalized_sql": query.normalized_sql,
                "cost": plan.total_cost if plan else 0.0,
                "rows": plan.total_rows if plan else 0,
                "file_path": loc.file_path if loc else "unknown",
                "line_number": loc.line_number if loc else 0,
                "function_name": loc.function_name if loc else None,
            }
            matches.append(match)

        return {
            "pattern": pattern,
            "matches": matches,
            "total_matches": len(matches),
        }

    def get_pattern_matches(
        self,
        pattern_id: str,
        codebase_id: int,
        db: Session,
    ) -> list[PatternMatch]:
        """
        Get all queries matching a pattern.

        Args:
            pattern_id: Pattern ID
            codebase_id: Codebase ID
            db: Database session

        Returns:
            List of PatternMatch objects
        """
        result = self.analyze_codebase_patterns(codebase_id, db)

        # Find pattern
        pattern_dict = next((p for p in result["patterns"] if p["pattern_id"] == pattern_id), None)

        if not pattern_dict:
            return []

        # Reconstruct QueryPattern
        pattern = QueryPattern(
            pattern_id=pattern_dict["pattern_id"],
            pattern_type=pattern_dict["pattern_type"],
            pattern_signature=pattern_dict["pattern_signature"],
            query_count=pattern_dict["query_count"],
            files_impacted=pattern_dict["files_impacted"],
            total_cost=pattern_dict["total_cost"],
            max_cost=pattern_dict["max_cost"],
            avg_cost=pattern_dict["avg_cost"],
            total_rows=pattern_dict["total_rows"],
            max_rows=pattern_dict["max_rows"],
            avg_rows=pattern_dict["avg_rows"],
            risk_score=pattern_dict["risk_score"],
            severity=pattern_dict["severity"],
            sample_query_id=pattern_dict["sample_query_id"],
            metadata=pattern_dict["metadata"],
        )

        # Get matching queries
        query_ids = pattern.meta_data.get("query_ids", [])
        queries = db.query(ExtractedQuery).filter(ExtractedQuery.id.in_(query_ids)).all()

        return self.duplicate_detector.get_pattern_matches(pattern, queries, db)

    def get_files_impacted_by_pattern(
        self,
        pattern_id: str,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Get files impacted by a specific pattern.

        Args:
            pattern_id: Pattern ID
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Dictionary with file impact information
        """
        pattern_details = self.get_pattern_details(pattern_id, codebase_id, db)

        if "error" in pattern_details:
            return pattern_details

        # Group matches by file
        file_impacts: dict[str, list[dict[str, Any]]] = {}

        for match in pattern_details["matches"]:
            file_path = match["file_path"]
            if file_path not in file_impacts:
                file_impacts[file_path] = []
            file_impacts[file_path].append(match)

        # Calculate file statistics
        file_stats = []
        for file_path, matches in file_impacts.items():
            total_cost = sum(m["cost"] for m in matches)
            total_rows = sum(m["rows"] for m in matches)

            file_stats.append(
                {
                    "file_path": file_path,
                    "query_count": len(matches),
                    "total_cost": total_cost,
                    "total_rows": total_rows,
                    "avg_cost": total_cost / len(matches) if matches else 0.0,
                }
            )

        # Sort by total cost descending
        file_stats.sort(key=lambda x: x["total_cost"], reverse=True)

        return {
            "pattern_id": pattern_id,
            "total_files": len(file_stats),
            "file_impacts": file_stats,
        }

    def calculate_refactoring_potential(
        self,
        pattern_id: str,
        codebase_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Calculate potential savings from refactoring a pattern.

        Args:
            pattern_id: Pattern ID
            codebase_id: Codebase ID
            db: Database session

        Returns:
            Refactoring potential analysis
        """
        pattern_details = self.get_pattern_details(pattern_id, codebase_id, db)

        if "error" in pattern_details:
            return pattern_details

        pattern = pattern_details["pattern"]
        matches = pattern_details["matches"]

        # Calculate current total cost
        current_total_cost = sum(m["cost"] for m in matches)

        # Estimate potential savings
        # If duplicate, could consolidate to single query
        if pattern["pattern_type"] == "duplicate":
            # Assume 80% savings by consolidating duplicates
            estimated_savings = current_total_cost * 0.8
            consolidation_opportunity = True
        else:
            # Assume 30% savings by optimizing pattern
            estimated_savings = current_total_cost * 0.3
            consolidation_opportunity = False

        return {
            "pattern_id": pattern_id,
            "current_total_cost": current_total_cost,
            "estimated_savings": estimated_savings,
            "savings_percentage": round((estimated_savings / current_total_cost * 100) if current_total_cost > 0 else 0, 2),
            "consolidation_opportunity": consolidation_opportunity,
            "queries_affected": len(matches),
            "files_affected": len(set(m["file_path"] for m in matches)),
        }

    def _calculate_statistics(
        self,
        queries: list[ExtractedQuery],
        patterns: list[QueryPattern],
    ) -> PatternStatistics:
        """
        Calculate pattern statistics.

        Args:
            queries: List of queries
            patterns: List of patterns

        Returns:
            Pattern statistics
        """
        total_patterns = len(patterns)
        duplicate_patterns = len([p for p in patterns if p.pattern_type == "duplicate"])
        expensive_patterns = len([p for p in patterns if p.pattern_type == "expensive"])
        anti_patterns = len([p for p in patterns if p.pattern_type == "anti_pattern"])
        common_patterns = len([p for p in patterns if p.pattern_type == "common"])

        total_queries_analyzed = len(queries)

        # Count unique queries in patterns
        queries_in_patterns = set()
        for pattern in patterns:
            query_ids = pattern.meta_data.get("query_ids", [])
            queries_in_patterns.update(query_ids)

        unique_queries = len(queries_in_patterns)

        avg_queries_per_pattern = total_queries_analyzed / total_patterns if total_patterns > 0 else 0.0

        high_risk_patterns = len([p for p in patterns if p.risk_score >= 75])
        medium_risk_patterns = len([p for p in patterns if 50 <= p.risk_score < 75])
        low_risk_patterns = len([p for p in patterns if p.risk_score < 50])

        return PatternStatistics(
            total_patterns=total_patterns,
            duplicate_patterns=duplicate_patterns,
            expensive_patterns=expensive_patterns,
            anti_patterns=anti_patterns,
            common_patterns=common_patterns,
            total_queries_analyzed=total_queries_analyzed,
            queries_in_patterns=len(queries_in_patterns),
            unique_queries=unique_queries,
            avg_queries_per_pattern=round(avg_queries_per_pattern, 2),
            high_risk_patterns=high_risk_patterns,
            medium_risk_patterns=medium_risk_patterns,
            low_risk_patterns=low_risk_patterns,
        )

    def _create_empty_statistics(self) -> PatternStatistics:
        """Create empty statistics."""
        return PatternStatistics(
            total_patterns=0,
            duplicate_patterns=0,
            expensive_patterns=0,
            anti_patterns=0,
            common_patterns=0,
            total_queries_analyzed=0,
            queries_in_patterns=0,
            unique_queries=0,
            avg_queries_per_pattern=0.0,
            high_risk_patterns=0,
            medium_risk_patterns=0,
            low_risk_patterns=0,
        )
