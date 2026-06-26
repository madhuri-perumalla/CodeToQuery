"""AST query grouping engine module."""
from app.services.grouping.duplicate_detector import DuplicateDetector
from app.services.grouping.pattern_detector import PatternDetector
from app.services.grouping.pattern_grouping_service import PatternGroupingService
from app.services.grouping.query_pattern import PatternMatch, PatternStatistics, QueryPattern
from app.services.grouping.structural_comparator import StructuralComparator

__all__ = [
    "QueryPattern",
    "PatternMatch",
    "PatternStatistics",
    "StructuralComparator",
    "DuplicateDetector",
    "PatternDetector",
    "PatternGroupingService",
]
