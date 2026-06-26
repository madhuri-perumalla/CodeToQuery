"""Diagnostic rule engine module."""
from app.services.diagnostics.code_aware_diagnostics import (
    CodeAwareDiagnostic,
    CodeAwareDiagnosticsService,
    SourceContext,
)
from app.services.diagnostics.rule_engine import DiagnosticResult, DiagnosticRule, RuleEngine, rule_engine
from app.services.diagnostics.rule_registry import register_default_rules
from app.services.diagnostics.rules.expensive_join_rule import ExpensiveJoinRule
from app.services.diagnostics.rules.full_table_scan_rule import FullTableScanRule
from app.services.diagnostics.rules.high_cost_rule import HighCostRule
from app.services.diagnostics.rules.high_row_estimate_rule import HighRowEstimateRule
from app.services.diagnostics.rules.missing_index_rule import MissingIndexRule
from app.services.diagnostics.rules.sequential_scan_rule import SequentialScanRule
from app.services.diagnostics.rules.sort_cost_rule import SortCostRule

__all__ = [
    "DiagnosticResult",
    "DiagnosticRule",
    "RuleEngine",
    "rule_engine",
    "register_default_rules",
    "FullTableScanRule",
    "SequentialScanRule",
    "MissingIndexRule",
    "HighCostRule",
    "ExpensiveJoinRule",
    "HighRowEstimateRule",
    "SortCostRule",
    "SourceContext",
    "CodeAwareDiagnostic",
    "CodeAwareDiagnosticsService",
]
