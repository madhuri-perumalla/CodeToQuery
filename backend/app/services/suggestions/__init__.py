"""Fix suggestion engine module."""
from app.services.suggestions.filter_optimizer import FilterOptimization, FilterOptimizer
from app.services.suggestions.index_recommender import IndexRecommendation, IndexRecommender
from app.services.suggestions.query_rewrite_advisor import QueryRewriteAdvisor, RewriteSuggestion
from app.services.suggestions.suggestion_service import SuggestionService

__all__ = [
    "IndexRecommendation",
    "IndexRecommender",
    "RewriteSuggestion",
    "QueryRewriteAdvisor",
    "FilterOptimization",
    "FilterOptimizer",
    "SuggestionService",
]
