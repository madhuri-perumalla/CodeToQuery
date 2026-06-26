"""Query normalization service module."""
from app.services.normalization.ast_normalizer import ASTNormalizer
from app.services.normalization.duplicate_detector import DuplicateDetector
from app.services.normalization.sql_parser import SQLParser
from app.services.normalization.structural_comparison import StructuralComparison

__all__ = [
    "SQLParser",
    "ASTNormalizer",
    "StructuralComparison",
    "DuplicateDetector",
]
