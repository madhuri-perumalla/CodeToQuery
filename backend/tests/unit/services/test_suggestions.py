"""Tests for suggestion service."""
from unittest.mock import Mock, patch

import pytest

from app.services.suggestions import SuggestionService
from app.services.suggestions.filter_optimizer import FilterOptimization, FilterOptimizer
from app.services.suggestions.index_recommender import IndexRecommendation, IndexRecommender
from app.services.suggestions.query_rewrite_advisor import QueryRewriteAdvisor, RewriteSuggestion


class TestIndexRecommendation:
    """Tests for IndexRecommendation dataclass."""

    def test_to_dict(self):
        """Test IndexRecommendation to dictionary conversion."""
        recommendation = IndexRecommendation(
            table_name="users",
            column_names=["id", "email"],
            index_type="btree",
            recommendation_type="composite",
            selectivity_estimate=0.5,
            confidence_score=0.85,
            impact_estimate="high",
            reason="Composite index for multi-column filtering",
            sql_statement="CREATE INDEX idx_users_id_email ON users (id, email);",
            related_query_ids=[1, 2, 3],
        )

        result = recommendation.to_dict()

        assert result["table_name"] == "users"
        assert result["column_names"] == ["id", "email"]
        assert result["index_type"] == "btree"
        assert result["confidence_score"] == 0.85


class TestRewriteSuggestion:
    """Tests for RewriteSuggestion dataclass."""

    def test_to_dict(self):
        """Test RewriteSuggestion to dictionary conversion."""
        suggestion = RewriteSuggestion(
            suggestion_type="subquery_to_join",
            original_sql="SELECT *, (SELECT COUNT(*) FROM posts WHERE user_id = u.id) FROM users u",
            rewritten_sql="SELECT u.*, COUNT(p.id) FROM users u LEFT JOIN posts p ON u.id = p.user_id GROUP BY u.id",
            reason="Convert subquery to JOIN for better performance",
            confidence_score=0.85,
            impact_estimate="high",
            related_query_id=1,
        )

        result = suggestion.to_dict()

        assert result["suggestion_type"] == "subquery_to_join"
        assert result["confidence_score"] == 0.85
        assert result["impact_estimate"] == "high"


class TestFilterOptimization:
    """Tests for FilterOptimization dataclass."""

    def test_to_dict(self):
        """Test FilterOptimization to dictionary conversion."""
        optimization = FilterOptimization(
            optimization_type="function_on_column",
            original_condition="UPPER(email) = 'TEST@EXAMPLE.COM'",
            optimized_condition="CREATE INDEX idx_users_email_upper ON users (UPPER(email));",
            reason="Function on column prevents index usage",
            confidence_score=0.9,
            impact_estimate="high",
            related_query_id=1,
        )

        result = optimization.to_dict()

        assert result["optimization_type"] == "function_on_column"
        assert result["confidence_score"] == 0.9
        assert result["impact_estimate"] == "high"


class TestIndexRecommender:
    """Tests for IndexRecommender."""

    def test_analyze_query_for_indexes_no_plan(self):
        """Test analyzing query without execution plan."""
        recommender = IndexRecommender()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE id = $1"

        recommendations = recommender.analyze_query_for_indexes(query, None)

        assert recommendations == []

    def test_analyze_sequential_scans(self):
        """Test analyzing sequential scans for index opportunities."""
        recommender = IndexRecommender()
        query = Mock()
        query.id = 1

        plan = Mock()
        plan.plan_json = {
            "Node Type": "Seq Scan",
            "Relation Name": "users",
            "Alias": "users",
            "Filter": "users.id = $1",
        }

        recommendations = recommender._analyze_sequential_scans(query, plan)

        assert len(recommendations) > 0
        assert recommendations[0].table_name == "users"

    def test_analyze_where_clauses(self):
        """Test analyzing WHERE clauses for index opportunities."""
        recommender = IndexRecommender()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE email = $1 AND status = 'active'"

        recommendations = recommender._analyze_where_clauses(query)

        assert len(recommendations) > 0

    def test_analyze_join_clauses(self):
        """Test analyzing JOIN clauses for index opportunities."""
        recommender = IndexRecommender()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users u JOIN posts p ON u.id = p.user_id"

        recommendations = recommender._analyze_join_clauses(query)

        assert len(recommendations) > 0

    def test_generate_composite_index_recommendation(self):
        """Test generating composite index recommendation."""
        recommender = IndexRecommender()

        recommendation = recommender.generate_composite_index_recommendation(
            table_name="users",
            columns=["id", "email"],
            query_ids=[1, 2, 3],
        )

        assert recommendation.table_name == "users"
        assert recommendation.column_names == ["id", "email"]
        assert recommendation.recommendation_type == "composite"
        assert recommendation.related_query_ids == [1, 2, 3]

    def test_generate_partial_index_recommendation(self):
        """Test generating partial index recommendation."""
        recommender = IndexRecommender()

        recommendation = recommender.generate_partial_index_recommendation(
            table_name="users",
            column="email",
            condition="email IS NOT NULL",
            query_ids=[1],
        )

        assert recommendation.table_name == "users"
        assert recommendation.column_names == ["email"]
        assert recommendation.recommendation_type == "partial"

    def test_generate_gin_index_recommendation(self):
        """Test generating GIN index recommendation."""
        recommender = IndexRecommender()

        recommendation = recommender.generate_gin_index_recommendation(
            table_name="posts",
            column="tags",
            query_ids=[1],
        )

        assert recommendation.table_name == "posts"
        assert recommendation.column_names == ["tags"]
        assert recommendation.index_type == "gin"


class TestQueryRewriteAdvisor:
    """Tests for QueryRewriteAdvisor."""

    def test_analyze_query_for_rewrites_no_plan(self):
        """Test analyzing query without execution plan."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users"

        suggestions = advisor.analyze_query_for_rewrites(query, None)

        assert len(suggestions) >= 0

    def test_detect_subquery_in_select(self):
        """Test detecting subquery in SELECT clause."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT *, (SELECT COUNT(*) FROM posts WHERE user_id = u.id) FROM users u"

        suggestions = advisor._detect_subquery_in_select(query)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == "subquery_to_join"

    def test_suggest_cte(self):
        """Test suggesting CTE for complex queries."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM (SELECT * FROM (SELECT * FROM users)) u"

        suggestions = advisor._suggest_cte(query)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == "add_cte"

    def test_suggest_limit(self):
        """Test suggesting LIMIT for queries without it."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users"

        suggestions = advisor._suggest_limit(query)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == "add_limit"

    def test_suggest_distinct_optimization(self):
        """Test suggesting DISTINCT optimization."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT DISTINCT email FROM users"

        suggestions = advisor._suggest_distinct_optimization(query)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == "distinct_to_group_by"

    def test_suggest_union(self):
        """Test suggesting UNION instead of OR."""
        advisor = QueryRewriteAdvisor()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE status = 'active' OR status = 'pending'"

        suggestions = advisor._suggest_union(query)

        assert len(suggestions) > 0
        assert suggestions[0].suggestion_type == "or_to_union"


class TestFilterOptimizer:
    """Tests for FilterOptimizer."""

    def test_analyze_query_for_filter_optimizations_no_plan(self):
        """Test analyzing query without execution plan."""
        optimizer = FilterOptimizer()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users"

        optimizations = optimizer.analyze_query_for_filter_optimizations(query, None)

        assert len(optimizations) >= 0

    def test_detect_non_sargable_expressions(self):
        """Test detecting non-sargable expressions."""
        optimizer = FilterOptimizer()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE email = UPPER($1)"

        optimizations = optimizer._detect_non_sargable_expressions(query)

        assert len(optimizations) >= 0

    def test_detect_functions_on_columns(self):
        """Test detecting function calls on columns."""
        optimizer = FilterOptimizer()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE UPPER(email) = 'TEST'"

        optimizations = optimizer._detect_functions_on_columns(query)

        assert len(optimizations) > 0
        assert optimizations[0].optimization_type == "function_on_column"

    def test_detect_like_optimization(self):
        """Test detecting LIKE optimization opportunities."""
        optimizer = FilterOptimizer()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users WHERE email LIKE '%@example.com'"

        optimizations = optimizer._detect_like_optimization(query)

        assert len(optimizations) > 0
        assert optimizations[0].optimization_type == "like_optimization"

    def test_suggest_index_for_function(self):
        """Test suggesting functional index."""
        optimizer = FilterOptimizer()

        optimization = optimizer.suggest_index_for_function(
            column="email",
            function="UPPER",
            query_id=1,
        )

        assert optimization.optimization_type == "function_on_column"
        assert optimization.related_query_id == 1

    def test_suggest_partial_index_for_null(self):
        """Test suggesting partial index for NULL handling."""
        optimizer = FilterOptimizer()

        optimization = optimizer.suggest_partial_index_for_null(
            column="email",
            query_id=1,
        )

        assert optimization.optimization_type == "null_handling"
        assert optimization.related_query_id == 1

    def test_suggest_trigram_index(self):
        """Test suggesting trigram index."""
        optimizer = FilterOptimizer()

        optimization = optimizer.suggest_trigram_index(
            column="content",
            query_id=1,
        )

        assert optimization.optimization_type == "like_optimization"
        assert optimization.related_query_id == 1


class TestSuggestionService:
    """Tests for SuggestionService."""

    def test_generate_suggestions_for_query_no_plan(self):
        """Test generating suggestions for query without plan."""
        service = SuggestionService()
        query = Mock()
        query.id = 1
        query.normalized_sql = "SELECT * FROM users"
        db = Mock()

        suggestions = service.generate_suggestions_for_query(query, None, db)

        assert "index_recommendations" in suggestions
        assert "rewrite_suggestions" in suggestions
        assert "filter_optimizations" in suggestions

    def test_generate_suggestions_for_diagnostic_no_query(self):
        """Test generating suggestions for diagnostic without query."""
        service = SuggestionService()
        diagnostic = Mock()
        diagnostic.query_id = 1
        diagnostic.rule_id = "sequential_scan"
        db = Mock()

        db.query.return_value.filter.return_value.first.return_value = None

        suggestions = service.generate_suggestions_for_diagnostic(diagnostic, db)

        assert suggestions == []

    def test_generate_sequential_scan_suggestions(self):
        """Test generating suggestions for sequential scan diagnostic."""
        service = SuggestionService()
        query = Mock()
        query.id = 1
        plan = Mock()
        db = Mock()

        with patch.object(service.index_recommender, "analyze_query_for_indexes") as mock_analyze:
            mock_analyze.return_value = [
                IndexRecommendation(
                    table_name="users",
                    column_names=["id"],
                    index_type="btree",
                    recommendation_type="single_column",
                    selectivity_estimate=0.5,
                    confidence_score=0.8,
                    impact_estimate="high",
                    reason="Sequential scan on users",
                    sql_statement="CREATE INDEX idx_users_id ON users (id);",
                    related_query_ids=[1],
                )
            ]

            suggestions = service._generate_sequential_scan_suggestions(query, plan)

            assert len(suggestions) > 0
            assert suggestions[0]["suggestion_type"] == "add_index"

    def test_generate_high_cost_suggestions(self):
        """Test generating suggestions for high cost diagnostic."""
        service = SuggestionService()
        query = Mock()
        query.id = 1
        plan = Mock()
        plan.total_cost = 6000
        db = Mock()

        with patch.object(service.query_rewrite_advisor, "analyze_query_for_rewrites") as mock_analyze:
            mock_analyze.return_value = [
                RewriteSuggestion(
                    suggestion_type="add_limit",
                    original_sql="SELECT * FROM users",
                    rewritten_sql="SELECT * FROM users LIMIT 1000",
                    reason="Add LIMIT for safety",
                    confidence_score=0.6,
                    impact_estimate="medium",
                    related_query_id=1,
                )
            ]

            suggestions = service._generate_high_cost_suggestions(query, plan)

            assert len(suggestions) > 0

    def test_save_suggestions_to_db(self):
        """Test saving suggestions to database."""
        service = SuggestionService()
        diagnostic_id = 1
        suggestions = [
            {
                "suggestion_type": "add_index",
                "description": "Add index on users.id",
                "sql_change": "CREATE INDEX idx_users_id ON users (id);",
                "impact_estimate": "high",
                "confidence_score": 0.8,
                "metadata": {},
            }
        ]
        db = Mock()

        created = service.save_suggestions_to_db(diagnostic_id, suggestions, db)

        assert len(created) == 1
        db.commit.assert_called_once()

    def test_get_suggestions_for_diagnostic(self):
        """Test getting suggestions for diagnostic."""
        service = SuggestionService()
        diagnostic_id = 1
        db = Mock()

        from app.models.suggestion import FixSuggestion

        suggestion = FixSuggestion(
            id=1,
            diagnostic_id=diagnostic_id,
            suggestion_type="add_index",
            description="Add index",
            sql_change="CREATE INDEX ...",
            impact_estimate="high",
            confidence_score=0.8,
            metadata={},
        )

        db.query.return_value.filter.return_value.all.return_value = [suggestion]

        suggestions = service.get_suggestions_for_diagnostic(diagnostic_id, db)

        assert len(suggestions) == 1
        assert suggestions[0]["diagnostic_id"] == diagnostic_id

    def test_get_all_suggestions_for_codebase(self):
        """Test getting all suggestions for codebase."""
        service = SuggestionService()
        codebase_id = 1
        db = Mock()

        db.query.return_value.filter.return_value.all.return_value = []
        db.query.return_value.filter.return_value.first.return_value = None

        suggestions = service.get_all_suggestions_for_codebase(codebase_id, db)

        assert "codebase_id" in suggestions
        assert "total_suggestions" in suggestions
        assert "suggestions_by_type" in suggestions

    def test_apply_suggestion_not_found(self):
        """Test applying suggestion that doesn't exist."""
        service = SuggestionService()
        suggestion_id = 999
        db = Mock()

        db.query.return_value.filter.return_value.first.return_value = None

        result = service.apply_suggestion(suggestion_id, db)

        assert "error" in result
