"""
Scenario generator and stress-testing engine for the orbital fuel depot.
Strictly implements:
- BASE (standard case inputs)
- HIGH_DEMAND and LOW_DEMAND (proportional critical demand scaling)
- MANDATORY_STRESS (the official hackathon stress test:
    * 2038-2040: Total & Critical demand * 1.15
    * 2038-2039: Earth-Core and Earth-Flex variable price * 1.25
    * 2038-2040: Lunar-ISRU actual delivery = 55% (2038), 75% (2039), 100% (2040) of plan
    * Storage loss ceiling <= 2.0% of throughput from 2038 (mandates ZBO compliance)
)
- GEOPOLITICAL_SHOCK (bonus research module): customizable price multipliers and delivery caps.
"""

from enum import Enum
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field
from src.core.constants import (
    ChannelID,
    DemandRecord,
    BASE_DEMAND,
    EXTENDED_DEMAND,
    SimulationConfig,
    YearlyPlan,
)
from src.core.balance import calculate_material_balance, SimulationBalanceResult
from src.core.economics import calculate_economics, SimulationEconomicsResult
from src.core.constraints import validate_constraints, ConstraintCheckResult


class ScenarioType(str, Enum):
    BASELINE = "Baseline"
    HIGH_DEMAND = "High Demand"
    LOW_DEMAND = "Low Demand"
    MANDATORY_STRESS = "Mandatory Stress"
    GEOPOLITICAL_SHOCK = "Geopolitical Shock"


class GeopoliticalShockConfig(BaseModel):
    """
    Configuration parameters for the Geopolitical bonus research scenario.
    """
    start_year: int = Field(2037, ge=2035, le=2045)
    end_year: int = Field(2039, ge=2035, le=2045)
    earth_core_price_multiplier: float = Field(1.35, ge=0.5, le=3.0, description="Launch & fuel tariff surcharge")
    earth_flex_price_multiplier: float = Field(1.40, ge=0.5, le=3.0, description="Flex spot tariff surcharge")
    earth_core_capacity_cap: Optional[float] = Field(None, gt=0.0, description="Sanctions launch limit (t/yr)")
    description: str = Field(
        "Geopolitical export licensing embargo and commercial launch insurance premium surge.",
        description="Scenario storyline narrative",
    )


class ScenarioModifier(BaseModel):
    """
    Concrete numerical modifications for a scenario across the simulation horizon.
    """
    scenario_type: ScenarioType
    name: str
    description: str
    demand: Dict[int, DemandRecord]
    price_multipliers: Dict[int, Dict[ChannelID, float]] = Field(default_factory=dict)
    delivery_multipliers: Dict[int, Dict[ChannelID, float]] = Field(default_factory=dict)
    max_allowed_throughput_loss: Optional[Dict[int, float]] = Field(
        default_factory=dict, description="Mandatory loss ceiling by year (e.g. <= 2% in stress)"
    )


def get_scenario_modifier(
    scenario_type: ScenarioType,
    config: SimulationConfig,
    geo_config: Optional[GeopoliticalShockConfig] = None,
) -> ScenarioModifier:
    """
    Builds the exact scenario modifier corresponding to the official rules.
    """
    raw_demand = EXTENDED_DEMAND if config.end_year > 2040 else BASE_DEMAND
    demand_dict: Dict[int, DemandRecord] = {}
    price_mult: Dict[int, Dict[ChannelID, float]] = {}
    deliv_mult: Dict[int, Dict[ChannelID, float]] = {}
    loss_ceiling: Dict[int, float] = {}

    if scenario_type == ScenarioType.BASELINE:
        # Standard unperturbed case inputs
        for y in config.horizon:
            rec = raw_demand[y]
            demand_dict[y] = DemandRecord(
                year=y,
                base_total=rec.base_total,
                base_critical=rec.base_critical,
                low_total=rec.low_total,
                high_total=rec.high_total,
            )
            price_mult[y] = {ch: 1.0 for ch in ChannelID}
            deliv_mult[y] = {ch: 1.0 for ch in ChannelID}

        return ScenarioModifier(
            scenario_type=ScenarioType.BASELINE,
            name="Baseline Scenario",
            description="Standard nominal case parameters with deterministic deliveries.",
            demand=demand_dict,
            price_multipliers=price_mult,
            delivery_multipliers=deliv_mult,
        )

    elif scenario_type == ScenarioType.HIGH_DEMAND:
        # High demand: high_total used, critical demand scaled proportionally
        for y in config.horizon:
            rec = raw_demand[y]
            ht = rec.high_total if rec.high_total is not None else rec.base_total * 1.25
            crit_ht = rec.base_critical * (ht / rec.base_total)
            demand_dict[y] = DemandRecord(
                year=y,
                base_total=round(ht, 4),
                base_critical=round(crit_ht, 4),
                low_total=rec.low_total,
                high_total=rec.high_total,
            )
            price_mult[y] = {ch: 1.0 for ch in ChannelID}
            deliv_mult[y] = {ch: 1.0 for ch in ChannelID}

        return ScenarioModifier(
            scenario_type=ScenarioType.HIGH_DEMAND,
            name="High Demand Scenario",
            description="Stress on infrastructure through rapid mission growth (proportional critical demand).",
            demand=demand_dict,
            price_multipliers=price_mult,
            delivery_multipliers=deliv_mult,
        )

    elif scenario_type == ScenarioType.LOW_DEMAND:
        # Low demand: low_total used, critical demand scaled proportionally
        for y in config.horizon:
            rec = raw_demand[y]
            lt = rec.low_total if rec.low_total is not None else rec.base_total * 0.80
            crit_lt = rec.base_critical * (lt / rec.base_total)
            demand_dict[y] = DemandRecord(
                year=y,
                base_total=round(lt, 4),
                base_critical=round(crit_lt, 4),
                low_total=rec.low_total,
                high_total=rec.high_total,
            )
            price_mult[y] = {ch: 1.0 for ch in ChannelID}
            deliv_mult[y] = {ch: 1.0 for ch in ChannelID}

        return ScenarioModifier(
            scenario_type=ScenarioType.LOW_DEMAND,
            name="Low Demand Scenario",
            description="Missions delayed or canceled; evaluates take-or-pay financial exposure and storage costs.",
            demand=demand_dict,
            price_multipliers=price_mult,
            delivery_multipliers=deliv_mult,
        )

    elif scenario_type == ScenarioType.MANDATORY_STRESS:
        # Official Hackathon Mandatory Stress:
        # 1. 2038-2040: Total and Critical demand * 1.15
        # 2. 2038-2039: Earth-Core and Earth-Flex variable prices * 1.25
        # 3. 2038-2040: Lunar-ISRU actual delivery = 55% (2038), 75% (2039), 100% (2040)
        # 4. Storage loss ceiling <= 2.0% from 2038
        for y in config.horizon:
            rec = raw_demand[y]
            if y >= 2038:
                demand_dict[y] = DemandRecord(
                    year=y,
                    base_total=round(rec.base_total * 1.15, 4),
                    base_critical=round(rec.base_critical * 1.15, 4),
                    low_total=rec.low_total,
                    high_total=rec.high_total,
                )
                loss_ceiling[y] = 0.02  # Max 2.0% loss rate
            else:
                demand_dict[y] = DemandRecord(
                    year=y,
                    base_total=rec.base_total,
                    base_critical=rec.base_critical,
                    low_total=rec.low_total,
                    high_total=rec.high_total,
                )

            # Price shocks
            p_dict = {ch: 1.0 for ch in ChannelID}
            if y in (2038, 2039):
                p_dict[ChannelID.EARTH_CORE] = 1.25
                p_dict[ChannelID.EARTH_FLEX] = 1.25
            price_mult[y] = p_dict

            # Delivery shocks
            d_dict = {ch: 1.0 for ch in ChannelID}
            if y == 2038:
                d_dict[ChannelID.LUNAR_ISRU] = 0.55
            elif y == 2039:
                d_dict[ChannelID.LUNAR_ISRU] = 0.75
            elif y >= 2040:
                d_dict[ChannelID.LUNAR_ISRU] = 1.00
            deliv_mult[y] = d_dict

        return ScenarioModifier(
            scenario_type=ScenarioType.MANDATORY_STRESS,
            name="Mandatory Stress Test",
            description=(
                "Combined stress: Demand +15% (2038+), Earth supply price +25% (2038-2039), "
                "Lunar-ISRU delivery bottleneck (55% in 2038, 75% in 2039), loss limit <=2%."
            ),
            demand=demand_dict,
            price_multipliers=price_mult,
            delivery_multipliers=deliv_mult,
            max_allowed_throughput_loss=loss_ceiling,
        )

    elif scenario_type == ScenarioType.GEOPOLITICAL_SHOCK:
        # Bonus module: Geopolitical event
        geo = geo_config or GeopoliticalShockConfig()
        for y in config.horizon:
            rec = raw_demand[y]
            demand_dict[y] = DemandRecord(
                year=y,
                base_total=rec.base_total,
                base_critical=rec.base_critical,
                low_total=rec.low_total,
                high_total=rec.high_total,
            )
            p_dict = {ch: 1.0 for ch in ChannelID}
            if geo.start_year <= y <= geo.end_year:
                p_dict[ChannelID.EARTH_CORE] = geo.earth_core_price_multiplier
                p_dict[ChannelID.EARTH_FLEX] = geo.earth_flex_price_multiplier
            price_mult[y] = p_dict
            deliv_mult[y] = {ch: 1.0 for ch in ChannelID}

        return ScenarioModifier(
            scenario_type=ScenarioType.GEOPOLITICAL_SHOCK,
            name="Geopolitical Disruption Shock",
            description=geo.description,
            demand=demand_dict,
            price_multipliers=price_mult,
            delivery_multipliers=deliv_mult,
        )

    raise ValueError(f"Unsupported scenario type: {scenario_type}")


class SimulationRunOutput(BaseModel):
    """
    Consolidated simulation execution output.
    """
    scenario_type: ScenarioType
    scenario_name: str
    balance: SimulationBalanceResult
    economics: SimulationEconomicsResult
    constraints: ConstraintCheckResult


def apply_scenario(
    plans: Dict[int, YearlyPlan],
    scenario_type: ScenarioType,
    config: SimulationConfig,
    geo_config: Optional[GeopoliticalShockConfig] = None,
) -> SimulationRunOutput:
    """
    Orchestrates full calculation: applies scenario modifiers -> runs balance -> runs economics -> validates constraints.
    """
    modifier = get_scenario_modifier(scenario_type, config, geo_config)

    # 1. Physical Balance
    balance_res = calculate_material_balance(
        plans=plans,
        demand=modifier.demand,
        config=config,
        actual_delivery_multipliers=modifier.delivery_multipliers,
    )

    # Check scenario-specific loss ceiling if defined
    if modifier.max_allowed_throughput_loss:
        for y, max_loss in modifier.max_allowed_throughput_loss.items():
            if y in balance_res.yearly_results:
                y_res = balance_res.yearly_results[y]
                # If actual loss rate exceeds ceiling, annotate overflow or deficit flag
                if y_res.throughput_loss_rate > (max_loss + 1e-6):
                    # We can mark it in the diagnostics
                    pass

    # 2. Economics
    economics_res = calculate_economics(
        plans=plans,
        balance_results=balance_res,
        config=config,
        price_multipliers=modifier.price_multipliers,
    )

    # 3. Constraint Validation
    constraints_res = validate_constraints(
        plans=plans,
        balance=balance_res,
        economics=economics_res,
        config=config,
    )

    # Add scenario loss ceiling check to constraints if applicable
    if modifier.max_allowed_throughput_loss:
        for y, max_loss in modifier.max_allowed_throughput_loss.items():
            if y in balance_res.yearly_results:
                actual_loss = balance_res.yearly_results[y].throughput_loss_rate
                if actual_loss > (max_loss + 1e-6):
                    from src.core.constraints import ConstraintViolation
                    viol = ConstraintViolation(
                        year=y,
                        rule_code="STRESS_LOSS_CEILING_BREACH",
                        rule_name="Потолок потерь при стресс-тесте",
                        expected=f"<={max_loss:.1%}",
                        actual=f"{actual_loss:.1%}",
                        message=(
                            f"Год {y}: Коэффициент потерь {actual_loss:.1%} превышает лимит стресс-сценария "
                            f"{max_loss:.1%}. Требуется обязательное внедрение ZBO для снижения потерь до <=1.2%."
                        ),
                        is_violated=True,
                    )
                    constraints_res.violations.append(viol)
                    constraints_res.all_checks.append(viol)
                    constraints_res.is_feasible = False
                    constraints_res.total_violations_count = len(constraints_res.violations)

    return SimulationRunOutput(
        scenario_type=scenario_type,
        scenario_name=modifier.name,
        balance=balance_res,
        economics=economics_res,
        constraints=constraints_res,
    )
