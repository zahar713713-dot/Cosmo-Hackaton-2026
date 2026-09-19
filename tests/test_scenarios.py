"""
Stress-testing and scenario verification tests.
Verifies Criteria 10 & 12 (Mandatory Stress, sensitivity, and constraint enforcement).
"""

import pytest
from src.core.constants import (
    ChannelID,
    BASE_DEMAND,
    DEFAULT_CHANNELS,
    SimulationConfig,
    YearlyPlan,
    ChannelOrder,
)
from src.core.balance import calculate_material_balance
from src.core.economics import calculate_economics
from src.core.constraints import validate_constraints
from src.core.scenarios import (
    ScenarioType,
    get_scenario_modifier,
    apply_scenario,
)


def get_base_plan_dict() -> dict[int, YearlyPlan]:
    """Helper to construct baseline plans."""
    plans = {}
    for y in range(2035, 2041):
        d_tot = BASE_DEMAND[y].base_total
        core_cap = min(190.0, d_tot * 0.6)
        flex_cap = min(110.0, max(0.0, (d_tot - core_cap) * 0.7))
        isru_cap = min(120.0, max(0.0, d_tot - core_cap - flex_cap)) if y >= 2038 else 0.0

        orders = {
            ChannelID.EARTH_CORE: ChannelOrder(
                channel_id=ChannelID.EARTH_CORE, reserved_capacity=core_cap, order_volume=core_cap
            ),
            ChannelID.EARTH_FLEX: ChannelOrder(
                channel_id=ChannelID.EARTH_FLEX, reserved_capacity=flex_cap, order_volume=flex_cap
            ),
            ChannelID.EARTH_NEW: ChannelOrder(
                channel_id=ChannelID.EARTH_NEW, reserved_capacity=0.0, order_volume=0.0
            ),
            ChannelID.LUNAR_ISRU: ChannelOrder(
                channel_id=ChannelID.LUNAR_ISRU, reserved_capacity=isru_cap, order_volume=isru_cap
            ),
            ChannelID.EMERGENCY: ChannelOrder(
                channel_id=ChannelID.EMERGENCY, reserved_capacity=20.0, order_volume=0.0
            ),
        }
        plans[y] = YearlyPlan(
            year=y,
            orders=orders,
            zbo_invested=(y >= 2036),
            isru_funded=(y >= 2037),
            isru_operational=(y >= 2038),
        )
    return plans


class TestScenariosVerification:
    def test_mandatory_stress_exact_rules(self):
        """
        Verify all mandatory stress modifiers:
        1. 2038-2040 demand * 1.15
        2. 2038-2039 price surcharge +25% on Earth-Core and Earth-Flex
        3. 2038-2040 ISRU delivery cuts: 55% in 2038, 75% in 2039, 100% in 2040
        """
        config = SimulationConfig(start_year=2035, end_year=2040)
        mod = get_scenario_modifier(ScenarioType.MANDATORY_STRESS, config)

        # 1. Demand * 1.15 from 2038
        for y in (2035, 2036, 2037):
            assert mod.demand[y].base_total == BASE_DEMAND[y].base_total
            assert mod.demand[y].base_critical == BASE_DEMAND[y].base_critical

        for y in (2038, 2039, 2040):
            exp_tot = round(BASE_DEMAND[y].base_total * 1.15, 4)
            exp_crit = round(BASE_DEMAND[y].base_critical * 1.15, 4)
            assert mod.demand[y].base_total == exp_tot
            assert mod.demand[y].base_critical == exp_crit

        # 2. Price multiplier +25% on Earth-Core and Flex in 2038 and 2039
        assert mod.price_multipliers[2038][ChannelID.EARTH_CORE] == 1.25
        assert mod.price_multipliers[2038][ChannelID.EARTH_FLEX] == 1.25
        assert mod.price_multipliers[2039][ChannelID.EARTH_CORE] == 1.25
        assert mod.price_multipliers[2039][ChannelID.EARTH_FLEX] == 1.25
        # In 2040: returns to nominal 1.00
        assert mod.price_multipliers[2040][ChannelID.EARTH_CORE] == 1.00
        assert mod.price_multipliers[2040][ChannelID.EARTH_FLEX] == 1.00

        # 3. ISRU actual deliveries
        assert mod.delivery_multipliers[2038][ChannelID.LUNAR_ISRU] == 0.55
        assert mod.delivery_multipliers[2039][ChannelID.LUNAR_ISRU] == 0.75
        assert mod.delivery_multipliers[2040][ChannelID.LUNAR_ISRU] == 1.00

    def test_loss_ceiling_breach_detection_in_stress(self):
        """
        Stress requirement: Storage loss ceiling <= 2.0% from 2038.
        If operator fails to invest in ZBO, storage loss rate remains 4.5% (Base storage),
        which breaches the 2.0% ceiling and MUST trigger a violation.
        """
        config = SimulationConfig(start_year=2035, end_year=2040)
        plans = get_base_plan_dict()
        
        # Disable ZBO upgrade across all years
        for y in plans:
            plans[y].zbo_invested = False

        output = apply_scenario(plans, ScenarioType.MANDATORY_STRESS, config)

        loss_violations = [v for v in output.constraints.violations if v.rule_code == "STRESS_LOSS_CEILING_BREACH"]
        assert len(loss_violations) >= 1
        assert any(v.year == 2038 for v in loss_violations)
        assert output.constraints.is_feasible is False
        assert "превышает лимит стресс-сценария" in loss_violations[0].message

    def test_capex_2037_limit_violation(self):
        """
        Rule: Cumulative CAPEX through end of 2037 <= 1800 M c.u.
        If an infeasible investment schedule commits > 1800 M c.u. before 2038,
        validation MUST flag the error.
        """
        config = SimulationConfig(start_year=2035, end_year=2040)
        plans = get_base_plan_dict()
        
        # Override CAPEX schedule to create a breach: 1950 M c.u. in 2037
        capex_override = {
            2037: {"isru": 1950.0, "zbo": 0.0, "earth_new": 0.0}
        }
        
        bal_res = calculate_material_balance(plans, BASE_DEMAND, config)
        econ_res = calculate_economics(plans, bal_res, config, capex_schedule_override=capex_override)
        con_res = validate_constraints(plans, bal_res, econ_res, config)

        capex_viols = [v for v in con_res.violations if v.rule_code == "CAPEX_2037_LIMIT"]
        assert len(capex_viols) == 1
        assert capex_viols[0].is_violated is True
        assert con_res.is_feasible is False
        assert "1800.0" in capex_viols[0].message and "лимит" in capex_viols[0].message.lower()

