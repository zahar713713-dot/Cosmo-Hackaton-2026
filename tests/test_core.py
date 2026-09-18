"""
Unit and integration tests for the orbital fuel depot planning core.
Verifies compliance with V01-V10 synthetic test vectors and case specifications.
"""

import pytest
from src.core.constants import (
    ChannelID,
    DemandRecord,
    SupplyChannelConfig,
    StorageConfig,
    BASE_DEMAND,
    BASE_STORAGE,
    ZBO_STORAGE,
    DEFAULT_CHANNELS,
    MIN_CRITICAL_SERVICE_LEVEL,
    MIN_TOTAL_SERVICE_LEVEL,
    MAX_CAPEX_2037,
    MAX_CAPEX_TOTAL,
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
    SimulationEconomicsResult,
)
from src.core.constraints import (
    validate_constraints,
    ConstraintCheckResult,
)
from src.core.scenarios import (
    ScenarioType,
    apply_scenario,
    get_scenario_modifier,
    GeopoliticalShockConfig,
)


def create_sample_plans(zbo_year: int = 2036, isru_year: int = 2038) -> dict[int, YearlyPlan]:
    """
    Constructs a structurally feasible decision plan for 2035-2040.
    """
    plans = {}
    for y in range(2035, 2041):
        d_tot = BASE_DEMAND[y].base_total
        
        # Dispatch logic to fulfill demand + losses:
        # Core: max 190
        core_cap = min(190.0, d_tot * 0.60)
        rem = d_tot - core_cap
        
        # Flex: max 110
        flex_cap = min(110.0, max(0.0, rem * 0.70))
        rem = max(0.0, rem - flex_cap)
        
        # Lunar-ISRU available from 2038: max 120
        isru_cap = min(120.0, rem) if y >= isru_year else 0.0
        rem = max(0.0, rem - isru_cap)
        
        # Earth-New if still needed or Flex buffer
        if rem > 0 and flex_cap + rem <= 110.0:
            flex_cap += rem
            rem = 0.0

        orders = {
            ChannelID.EARTH_CORE: ChannelOrder(
                channel_id=ChannelID.EARTH_CORE,
                reserved_capacity=round(core_cap, 2),
                order_volume=round(core_cap, 2),
            ),
            ChannelID.EARTH_FLEX: ChannelOrder(
                channel_id=ChannelID.EARTH_FLEX,
                reserved_capacity=round(flex_cap, 2),
                order_volume=round(flex_cap, 2),
            ),
            ChannelID.EARTH_NEW: ChannelOrder(
                channel_id=ChannelID.EARTH_NEW,
                reserved_capacity=0.0,
                order_volume=0.0,
            ),
            ChannelID.LUNAR_ISRU: ChannelOrder(
                channel_id=ChannelID.LUNAR_ISRU,
                reserved_capacity=round(isru_cap, 2),
                order_volume=round(isru_cap, 2),
            ),
            ChannelID.EMERGENCY: ChannelOrder(
                channel_id=ChannelID.EMERGENCY,
                reserved_capacity=20.0,
                order_volume=0.0,  # Standby reserve
            ),
        }

        plans[y] = YearlyPlan(
            year=y,
            orders=orders,
            zbo_invested=(y >= zbo_year),
            isru_funded=(y >= 2037),  # Funded prior to 2038
            isru_operational=(y >= isru_year),
            earth_new_option_purchased=False,
            earth_new_exercised=False,
            earth_new_operational=False,
        )
    return plans


class TestCoreConstantsAndPydantic:
    def test_demand_critical_subset_validation(self):
        """Validates that critical demand cannot exceed total demand."""
        # Valid record
        rec = DemandRecord(year=2035, base_total=100.0, base_critical=80.0)
        assert rec.base_critical <= rec.base_total

        # Invalid record: critical > total should raise ValueError
        with pytest.raises(ValueError):
            DemandRecord(year=2035, base_total=80.0, base_critical=100.0)

    def test_channel_order_within_reservation(self):
        """Order volume cannot exceed reserved capacity."""
        order = ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=80.0)
        assert order.order_volume <= order.reserved_capacity

        with pytest.raises(ValueError):
            ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=50.0, order_volume=60.0)


class TestMaterialBalance:
    def test_v01_material_balance_arithmetic(self):
        """
        V01 test:
        start_stock=10, delivered=30, losses=4.5% of 30 = 1.35, served=25
        end_stock = 10 + 30 - 1.35 - 25 = 13.65
        """
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=10.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=30.0, order_volume=30.0
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=25.0, base_critical=20.0)}

        result = calculate_material_balance(plans, demand, config)
        res_35 = result.yearly_results[2035]

        assert res_35.start_stock == 10.0
        assert res_35.gross_delivery == 30.0
        assert abs(res_35.losses - 1.35) < 1e-4
        assert res_35.served_demand_total == 25.0
        assert abs(res_35.end_stock - 13.65) < 1e-4
        assert res_35.deficit_total == 0.0

    def test_v02_shortage_vs_negative_inventory(self):
        """
        V02 test: Physical stock cannot go negative. Deficit is tracked separately.
        Demand = 100, Start = 10, Delivery = 50, Net inflow = 50 - 2.25 = 47.75.
        Available = 57.75.
        Served = 57.75.
        Deficit = 100 - 57.75 = 42.25.
        End Stock = 0.0 (NOT -42.25).
        """
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=10.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=50.0, order_volume=50.0
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=100.0, base_critical=80.0)}

        result = calculate_material_balance(plans, demand, config)
        res_35 = result.yearly_results[2035]

        assert res_35.end_stock == 0.0
        assert abs(res_35.deficit_total - 42.25) < 1e-4
        assert abs(res_35.served_demand_total - 57.75) < 1e-4

    def test_v06_losses_charged_once_on_throughput(self):
        """
        Losses are charged on gross delivery, never twice on ending inventory.
        ZBO loss rate is 1.2%, Base is 4.5%.
        """
        config = SimulationConfig(start_year=2035, end_year=2036, initial_stock_2035=15.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={ChannelID.EARTH_CORE: ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=100.0)},
                zbo_invested=False,  # 4.5%
            ),
            2036: YearlyPlan(
                year=2036,
                orders={ChannelID.EARTH_CORE: ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=100.0)},
                zbo_invested=True,   # 1.2%
            ),
        }
        demand = {
            2035: DemandRecord(year=2035, base_total=50.0, base_critical=40.0),
            2036: DemandRecord(year=2036, base_total=50.0, base_critical=40.0),
        }

        result = calculate_material_balance(plans, demand, config)
        assert abs(result.yearly_results[2035].losses - 4.5) < 1e-4
        assert abs(result.yearly_results[2036].losses - 1.2) < 1e-4


class TestEconomics:
    def test_v03_take_or_pay_calculation(self):
        """
        Take-or-pay rule for Earth-Core:
        Reserved = 100, TOP = 70% -> Minimum billable = 70.
        Case A: Order = 50 -> Billable = max(50, 70) = 70.
        Var payment = 70 * 6.2 = 434.0.
        Reservation payment = 0.45 * 100 = 45.0.
        Total channel payment = 479.0.
        """
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=10.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=50.0
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=50.0, base_critical=40.0)}
        bal_res = calculate_material_balance(plans, demand, config)
        econ_res = calculate_economics(plans, bal_res, config)

        core_cost = econ_res.yearly_economics[2035].channel_costs[ChannelID.EARTH_CORE]
        assert core_cost.take_or_pay_threshold == 70.0
        assert core_cost.billable_volume == 70.0
        assert abs(core_cost.variable_payment - 434.0) < 1e-4
        assert abs(core_cost.reservation_payment - 45.0) < 1e-4
        assert abs(core_cost.total_channel_payment - 479.0) < 1e-4

    def test_v04_no_double_top_when_order_exceeds_threshold(self):
        """
        Case B: Reserved = 100, Order = 80 -> Billable = max(80, 70) = 80.
        TOP does NOT add an extra charge on top of 80.
        Var payment = 80 * 6.2 = 496.0.
        """
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=10.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=80.0
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=80.0, base_critical=60.0)}
        bal_res = calculate_material_balance(plans, demand, config)
        econ_res = calculate_economics(plans, bal_res, config)

        core_cost = econ_res.yearly_economics[2035].channel_costs[ChannelID.EARTH_CORE]
        assert core_cost.billable_volume == 80.0
        assert abs(core_cost.variable_payment - 496.0) < 1e-4


class TestConstraintsAndScenarios:
    def test_full_baseline_simulation(self):
        """Executes full baseline and confirms feasibility with balanced plan."""
        config = SimulationConfig(start_year=2035, end_year=2040)
        plans = create_sample_plans()
        output = apply_scenario(plans, ScenarioType.BASELINE, config)

        assert output.scenario_type == ScenarioType.BASELINE
        assert output.balance.average_service_level_total >= MIN_TOTAL_SERVICE_LEVEL
        assert output.balance.average_service_level_critical >= MIN_CRITICAL_SERVICE_LEVEL

    def test_mandatory_stress_shocks_applied(self):
        """Verifies that Mandatory Stress applies demand +15%, prices +25%, and ISRU shocks."""
        config = SimulationConfig(start_year=2035, end_year=2040)
        mod = get_scenario_modifier(ScenarioType.MANDATORY_STRESS, config)

        # Demand +15% in 2038
        base_38 = BASE_DEMAND[2038].base_total
        assert abs(mod.demand[2038].base_total - round(base_38 * 1.15, 4)) < 1e-4

        # Price Core/Flex +25% in 2038 and 2039, normal in 2040
        assert mod.price_multipliers[2038][ChannelID.EARTH_CORE] == 1.25
        assert mod.price_multipliers[2039][ChannelID.EARTH_FLEX] == 1.25
        assert mod.price_multipliers[2040][ChannelID.EARTH_CORE] == 1.00

        # ISRU actual deliveries: 55% in 2038, 75% in 2039, 100% in 2040
        assert mod.delivery_multipliers[2038][ChannelID.LUNAR_ISRU] == 0.55
        assert mod.delivery_multipliers[2039][ChannelID.LUNAR_ISRU] == 0.75
        assert mod.delivery_multipliers[2040][ChannelID.LUNAR_ISRU] == 1.00

    def test_v07_reserve_45_days_violation(self):
        """Checks violation when initial stock and emergency standby do not satisfy 45 days."""
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=2.0)
        # Demand 2035 = 100, 45-day requirement = 12.33 t
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=100.0),
                    ChannelID.EMERGENCY: ChannelOrder(channel_id=ChannelID.EMERGENCY, reserved_capacity=0.0, order_volume=0.0),
                },
                zbo_invested=False,
            )
        }
        output = apply_scenario(plans, ScenarioType.BASELINE, config)
        viols = [v for v in output.constraints.violations if v.rule_code == "RESERVE_45_DAYS"]
        assert len(viols) == 1
        assert viols[0].is_violated is True

    def test_v08_tank_capacity_overflow(self):
        """Checks tank overflow when closing stock exceeds 70 t."""
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=50.0)
        # Demand 2035 = 100, Delivery = 150 -> Net = 143.25 -> Total avail = 193.25 -> Served = 100 -> End stock = 93.25 > 70
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(channel_id=ChannelID.EARTH_CORE, reserved_capacity=150.0, order_volume=150.0)
                },
                zbo_invested=False,  # Cap = 70
            )
        }
        output = apply_scenario(plans, ScenarioType.BASELINE, config)
        viols = [v for v in output.constraints.violations if v.rule_code == "STORAGE_CAPACITY_OVERFLOW"]
        assert len(viols) == 1
        assert viols[0].is_violated is True

    def test_v09_emergency_consecutive_years_violation(self):
        """Emergency cannot be used as base channel for > 2 consecutive years."""
        config = SimulationConfig(start_year=2035, end_year=2038)
        plans = create_sample_plans()
        # Make Emergency deliver 30 t (base channel) in 2035, 2036, 2037 (3 consecutive years)
        for y in (2035, 2036, 2037):
            plans[y].orders[ChannelID.EMERGENCY] = ChannelOrder(
                channel_id=ChannelID.EMERGENCY, reserved_capacity=30.0, order_volume=30.0
            )
        output = apply_scenario(plans, ScenarioType.BASELINE, config)
        viols = [v for v in output.constraints.violations if v.rule_code == "EMERGENCY_CONSECUTIVE_LIMIT"]
        assert len(viols) == 1
        assert viols[0].is_violated is True

    def test_v10_capex_2037_limit_violation(self):
        """Cumulative CAPEX through 2037 cannot exceed 1800 M c.u."""
        config = SimulationConfig(start_year=2035, end_year=2037)
        plans = create_sample_plans()
        # Override CAPEX schedule with 1900 M c.u. in 2037
        capex_override = {2037: {"isru": 1900.0, "zbo": 0.0, "earth_new": 0.0}}
        bal_res = calculate_material_balance(plans, BASE_DEMAND, config)
        econ_res = calculate_economics(plans, bal_res, config, capex_schedule_override=capex_override)
        con_res = validate_constraints(plans, bal_res, econ_res, config)

        viols = [v for v in con_res.violations if v.rule_code == "CAPEX_2037_LIMIT"]
        assert len(viols) == 1
        assert viols[0].is_violated is True

    def test_geopolitical_bonus_scenario(self):
        """Verifies bonus geopolitical shock with customized tariffs."""
        config = SimulationConfig(start_year=2035, end_year=2040)
        geo_cfg = GeopoliticalShockConfig(
            start_year=2037, end_year=2038, earth_core_price_multiplier=1.50
        )
        mod = get_scenario_modifier(ScenarioType.GEOPOLITICAL_SHOCK, config, geo_cfg)

        assert mod.price_multipliers[2037][ChannelID.EARTH_CORE] == 1.50
        assert mod.price_multipliers[2038][ChannelID.EARTH_CORE] == 1.50
        assert mod.price_multipliers[2039][ChannelID.EARTH_CORE] == 1.00
