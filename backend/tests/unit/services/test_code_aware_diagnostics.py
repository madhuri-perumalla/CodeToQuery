"""Tests for code-aware diagnostics service."""
from unittest.mock import Mock, patch

import pytest

from app.services.diagnostics import (
    CodeAwareDiagnostic,
    CodeAwareDiagnosticsService,
    SourceContext,
)


class TestSourceContext:
    """Tests for SourceContext."""

    def test_to_dict(self):
        """Test SourceContext to dictionary conversion."""
        context = SourceContext(
            file_path="userService.ts",
            line_number=42,
            column_number=10,
            function_name="getUser",
            class_name="UserService",
            context_snippet="const user = await db.query('SELECT * FROM users')",
            call_stack=[{"file": "main.ts", "line": 10, "function": "main"}],
        )

        result = context.to_dict()

        assert result["file_path"] == "userService.ts"
        assert result["line_number"] == 42
        assert result["column_number"] == 10
        assert result["function_name"] == "getUser"
        assert result["class_name"] == "UserService"
        assert result["context_snippet"] == "const user = await db.query('SELECT * FROM users')"
        assert result["call_stack"] == [{"file": "main.ts", "line": 10, "function": "main"}]


class TestCodeAwareDiagnostic:
    """Tests for CodeAwareDiagnostic."""

    def test_to_dict_with_source_context(self):
        """Test CodeAwareDiagnostic to dictionary conversion with source context."""
        source_context = SourceContext(
            file_path="userService.ts",
            line_number=42,
            column_number=10,
            function_name="getUser",
            class_name="UserService",
            context_snippet="const user = await db.query('SELECT * FROM users')",
            call_stack=[],
        )

        diagnostic = CodeAwareDiagnostic(
            rule_id="sequential_scan",
            severity="warning",
            explanation="Query performs full table scan on users table.",
            evidence={"node_type": "Seq Scan", "relation_name": "users"},
            recommendation="Add index on frequently filtered columns.",
            location={"node_type": "Seq Scan", "path": "0"},
            metadata={"rule_type": "sequential_scan"},
            source_context=source_context,
            query_id=1,
            plan_id=1,
        )

        result = diagnostic.to_dict()

        assert result["rule_id"] == "sequential_scan"
        assert result["severity"] == "warning"
        assert result["source_context"]["file_path"] == "userService.ts"
        assert result["source_context"]["line_number"] == 42
        assert result["query_id"] == 1
        assert result["plan_id"] == 1

    def test_to_dict_without_source_context(self):
        """Test CodeAwareDiagnostic to dictionary conversion without source context."""
        diagnostic = CodeAwareDiagnostic(
            rule_id="sequential_scan",
            severity="warning",
            explanation="Query performs full table scan on users table.",
            evidence={"node_type": "Seq Scan", "relation_name": "users"},
            recommendation="Add index on frequently filtered columns.",
            location={"node_type": "Seq Scan", "path": "0"},
            metadata={"rule_type": "sequential_scan"},
            source_context=None,
            query_id=1,
            plan_id=1,
        )

        result = diagnostic.to_dict()

        assert result["rule_id"] == "sequential_scan"
        assert result["source_context"] is None


class TestCodeAwareDiagnosticsService:
    """Tests for CodeAwareDiagnosticsService."""

    def test_generate_code_aware_diagnostics_with_source_context(self):
        """Test generating code-aware diagnostics with source context."""
        service = CodeAwareDiagnosticsService()

        # Mock database session
        db = Mock()

        # Mock execution plan
        plan = Mock()
        plan.id = 1
        plan.query_id = 1
        plan.plan_json = {"Node Type": "Seq Scan", "Relation Name": "users"}

        # Mock query
        query = Mock()
        query.id = 1
        query.codebase_id = 1

        # Mock location
        location = Mock()
        location.file_path = "userService.ts"
        location.line_number = 42
        location.column_number = 10
        location.function_name = "getUser"
        location.class_name = "UserService"
        location.context_snippet = "const user = await db.query('SELECT * FROM users')"
        location.call_stack = []

        # Setup database queries
        db.query.return_value.filter.return_value.first.side_effect = [plan, query]
        db.query.return_value.filter.return_value.all.return_value = [location]

        # Mock rule engine
        with patch("app.services.diagnostics.code_aware_diagnostics.rule_engine") as mock_engine:
            mock_result = Mock()
            mock_result.rule_id = "sequential_scan"
            mock_result.severity = "warning"
            mock_result.explanation = "Query performs full table scan on users table."
            mock_result.evidence = {"node_type": "Seq Scan"}
            mock_result.recommendation = "Add index."
            mock_result.location = {"node_type": "Seq Scan"}
            mock_result.metadata = {"rule_type": "sequential_scan"}
            mock_engine.evaluate_all.return_value = [mock_result]

            diagnostics = service.generate_code_aware_diagnostics(1, db)

            assert len(diagnostics) == 1
            assert diagnostics[0].source_context.file_path == "userService.ts"
            assert diagnostics[0].source_context.line_number == 42
            assert diagnostics[0].source_context.function_name == "getUser"

    def test_generate_code_aware_diagnostics_without_source_context(self):
        """Test generating code-aware diagnostics without source context."""
        service = CodeAwareDiagnosticsService()

        # Mock database session
        db = Mock()

        # Mock execution plan
        plan = Mock()
        plan.id = 1
        plan.query_id = 1
        plan.plan_json = {"Node Type": "Seq Scan", "Relation Name": "users"}

        # Mock query
        query = Mock()
        query.id = 1
        query.codebase_id = 1

        # Setup database queries
        db.query.return_value.filter.return_value.first.side_effect = [plan, query]
        db.query.return_value.filter.return_value.all.return_value = []

        # Mock rule engine
        with patch("app.services.diagnostics.code_aware_diagnostics.rule_engine") as mock_engine:
            mock_result = Mock()
            mock_result.rule_id = "sequential_scan"
            mock_result.severity = "warning"
            mock_result.explanation = "Query performs full table scan on users table."
            mock_result.evidence = {"node_type": "Seq Scan"}
            mock_result.recommendation = "Add index."
            mock_result.location = {"node_type": "Seq Scan"}
            mock_result.metadata = {"rule_type": "sequential_scan"}
            mock_engine.evaluate_all.return_value = [mock_result]

            diagnostics = service.generate_code_aware_diagnostics(1, db)

            assert len(diagnostics) == 1
            assert diagnostics[0].source_context is None

    def test_get_source_context_for_query(self):
        """Test getting source context for a query."""
        service = CodeAwareDiagnosticsService()

        # Mock database session
        db = Mock()

        # Mock location
        location = Mock()
        location.file_path = "userService.ts"
        location.line_number = 42
        location.column_number = 10
        location.function_name = "getUser"
        location.class_name = "UserService"
        location.context_snippet = "const user = await db.query('SELECT * FROM users')"
        location.call_stack = []

        db.query.return_value.filter.return_value.all.return_value = [location]

        context = service.get_source_context_for_query(1, db)

        assert context is not None
        assert context.file_path == "userService.ts"
        assert context.line_number == 42
        assert context.function_name == "getUser"

    def test_get_source_context_for_query_no_locations(self):
        """Test getting source context when no locations exist."""
        service = CodeAwareDiagnosticsService()

        # Mock database session
        db = Mock()
        db.query.return_value.filter.return_value.all.return_value = []

        context = service.get_source_context_for_query(1, db)

        assert context is None

    def test_format_diagnostic_message_with_function(self):
        """Test formatting diagnostic message with function name."""
        service = CodeAwareDiagnosticsService()

        source_context = SourceContext(
            file_path="userService.ts",
            line_number=42,
            column_number=10,
            function_name="getUser",
            class_name="UserService",
            context_snippet="const user = await db.query('SELECT * FROM users')",
            call_stack=[],
        )

        diagnostic = CodeAwareDiagnostic(
            rule_id="sequential_scan",
            severity="warning",
            explanation="Query performs full table scan on users table.",
            evidence={"node_type": "Seq Scan"},
            recommendation="Add index.",
            location={"node_type": "Seq Scan"},
            metadata={"rule_type": "sequential_scan"},
            source_context=source_context,
            query_id=1,
            plan_id=1,
        )

        message = service.format_diagnostic_message(diagnostic)

        assert "[WARNING]" in message
        assert "userService.ts:42" in message
        assert "getUser()" in message
        assert "Query performs full table scan" in message

    def test_format_diagnostic_message_without_function(self):
        """Test formatting diagnostic message without function name."""
        service = CodeAwareDiagnosticsService()

        source_context = SourceContext(
            file_path="userService.ts",
            line_number=42,
            column_number=10,
            function_name=None,
            class_name=None,
            context_snippet="const user = await db.query('SELECT * FROM users')",
            call_stack=[],
        )

        diagnostic = CodeAwareDiagnostic(
            rule_id="sequential_scan",
            severity="warning",
            explanation="Query performs full table scan on users table.",
            evidence={"node_type": "Seq Scan"},
            recommendation="Add index.",
            location={"node_type": "Seq Scan"},
            metadata={"rule_type": "sequential_scan"},
            source_context=source_context,
            query_id=1,
            plan_id=1,
        )

        message = service.format_diagnostic_message(diagnostic)

        assert "[WARNING]" in message
        assert "userService.ts:42" in message
        assert "Query performs full table scan" in message

    def test_format_diagnostic_message_without_context(self):
        """Test formatting diagnostic message without source context."""
        service = CodeAwareDiagnosticsService()

        diagnostic = CodeAwareDiagnostic(
            rule_id="sequential_scan",
            severity="warning",
            explanation="Query performs full table scan on users table.",
            evidence={"node_type": "Seq Scan"},
            recommendation="Add index.",
            location={"node_type": "Seq Scan"},
            metadata={"rule_type": "sequential_scan"},
            source_context=None,
            query_id=1,
            plan_id=1,
        )

        message = service.format_diagnostic_message(diagnostic)

        assert "[WARNING]" in message
        assert "Unknown location" in message
        assert "Query performs full table scan" in message
