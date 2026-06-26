"""Rule registry for default diagnostic rules."""
from app.services.diagnostics.rule_engine import rule_engine
from app.services.diagnostics.rules.expensive_join_rule import ExpensiveJoinRule
from app.services.diagnostics.rules.full_table_scan_rule import FullTableScanRule
from app.services.diagnostics.rules.high_cost_rule import HighCostRule
from app.services.diagnostics.rules.high_row_estimate_rule import HighRowEstimateRule
from app.services.diagnostics.rules.missing_index_rule import MissingIndexRule
from app.services.diagnostics.rules.sequential_scan_rule import SequentialScanRule
from app.services.diagnostics.rules.sort_cost_rule import SortCostRule


def register_default_rules() -> None:
    """Register default diagnostic rules with the rule engine."""
    # Full Table Scan Warning
    rule_engine.register_rule(
        FullTableScanRule(
            row_threshold=10000,
            severity="warning",
            enabled=True,
        )
    )

    # Sequential Scan Warning
    rule_engine.register_rule(
        SequentialScanRule(
            severity="warning",
            enabled=True,
        )
    )

    # Missing Index Warning
    rule_engine.register_rule(
        MissingIndexRule(
            severity="warning",
            enabled=True,
        )
    )

    # High Cost Warning
    rule_engine.register_rule(
        HighCostRule(
            threshold=1000.0,
            severity="warning",
            enabled=True,
        )
    )

    # Expensive Join Warning
    rule_engine.register_rule(
        ExpensiveJoinRule(
            threshold=500.0,
            severity="warning",
            enabled=True,
        )
    )

    # High Row Estimate Warning
    rule_engine.register_rule(
        HighRowEstimateRule(
            threshold=100000,
            severity="warning",
            enabled=True,
        )
    )

    # Sort Cost Warning
    rule_engine.register_rule(
        SortCostRule(
            threshold=200.0,
            severity="warning",
            enabled=True,
        )
    )
