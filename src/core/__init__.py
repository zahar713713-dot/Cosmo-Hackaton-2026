"""
Core mathematical and economic planning engine for the Cis-lunar Orbital Fuel Depot 2035-2040.
KosmoHackathon 2026.
"""

from src.core.constants import (
    DEFAULT_HORIZON,
    DAYS_IN_YEAR,
    RESERVE_DAYS,
    MIN_CRITICAL_SERVICE_LEVEL,
    MIN_TOTAL_SERVICE_LEVEL,
    MAX_CAPEX_2037,
    MAX_CAPEX_TOTAL,
    DEFAULT_DISCOUNT_RATE,
    ChannelID,
    DemandRecord,
    SupplyChannelConfig,
    StorageConfig,
    ChannelOrder,
    YearlyPlan,
    SimulationConfig,
)
from src.core.balance import (
    calculate_material_balance,
    YearlyBalanceResult,
    SimulationBalanceResult,
)
from src.core.economics import (
    calculate_economics,
    YearlyEconomicsResult,
    SimulationEconomicsResult,
)
from src.core.constraints import (
    validate_constraints,
    ConstraintCheckResult,
    ConstraintSummary,
)
from src.core.scenarios import (
    ScenarioType,
    ScenarioModifier,
    apply_scenario,
    get_scenario_modifier,
    SimulationRunOutput,
)
from src.core.exporter import (
    export_to_excel,
    export_to_csv,
    generate_summary_kpi_dataframe,
    generate_material_balance_dataframe,
    generate_economics_dataframe,
    generate_constraints_log_dataframe,
)

__all__ = [
    "DEFAULT_HORIZON",
    "DAYS_IN_YEAR",
    "RESERVE_DAYS",
    "MIN_CRITICAL_SERVICE_LEVEL",
    "MIN_TOTAL_SERVICE_LEVEL",
    "MAX_CAPEX_2037",
    "MAX_CAPEX_TOTAL",
    "DEFAULT_DISCOUNT_RATE",
    "ChannelID",
    "DemandRecord",
    "SupplyChannelConfig",
    "StorageConfig",
    "ChannelOrder",
    "YearlyPlan",
    "SimulationConfig",
    "calculate_material_balance",
    "YearlyBalanceResult",
    "SimulationBalanceResult",
    "calculate_economics",
    "YearlyEconomicsResult",
    "SimulationEconomicsResult",
    "validate_constraints",
    "ConstraintCheckResult",
    "ConstraintSummary",
    "ScenarioType",
    "ScenarioModifier",
    "apply_scenario",
    "get_scenario_modifier",
    "SimulationRunOutput",
    "export_to_excel",
    "export_to_csv",
    "generate_summary_kpi_dataframe",
    "generate_material_balance_dataframe",
    "generate_economics_dataframe",
    "generate_constraints_log_dataframe",
]
