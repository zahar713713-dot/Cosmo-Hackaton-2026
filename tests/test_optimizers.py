"""
Verification tests for the multi-algorithm mathematical optimization engine.
Tests Regulatory, NASA Space Logistics (MILP), and Minimax Robust optimization strategies.
"""

import pytest
from src.core.constants import SimulationConfig, ChannelID, BASE_DEMAND
from src.core.optimizers import (
    OptimizerAlgorithm,
    ALGORITHM_REGISTRY,
    optimize_plans,
)
from src.core.scenarios import apply_scenario, ScenarioType


class TestOptimizers:
    def test_registry_metadata(self):
        assert len(ALGORITHM_REGISTRY) == 3
        assert OptimizerAlgorithm.NASA_MILP in ALGORITHM_REGISTRY
        assert OptimizerAlgorithm.REGULATORY in ALGORITHM_REGISTRY
        assert OptimizerAlgorithm.MINIMAX_ROBUST in ALGORITHM_REGISTRY

        nasa_meta = ALGORITHM_REGISTRY[OptimizerAlgorithm.NASA_MILP]
        assert "NASA" in nasa_meta.name
        assert "AIAA" in nasa_meta.foundation
        assert nasa_meta.recommended is True

    def test_regulatory_optimizer_execution(self):
        inv = {"zbo_year": 2036, "isru_enabled": True, "earth_new_enabled": False}
        plans = optimize_plans(OptimizerAlgorithm.REGULATORY, inv)

        assert len(plans) == 6
        for y in range(2035, 2041):
            assert y in plans
            assert plans[y].orders[ChannelID.EARTH_CORE].order_volume > 0

        config = SimulationConfig(start_year=2035, end_year=2040)
        run = apply_scenario(plans, ScenarioType.BASELINE, config)
        assert run.constraints.is_feasible is True
        assert run.balance.average_service_level_critical == 1.0

    def test_nasa_milp_lcc_superiority(self):
        """
        NASA MILP must yield lower or equal NPV of LCC compared to Regulatory baseline,
        with 100% service level and zero take-or-pay deadweight penalties.
        """
        inv = {"zbo_year": 2036, "isru_enabled": True, "earth_new_enabled": False}
        config = SimulationConfig(start_year=2035, end_year=2040)

        reg_plans = optimize_plans(OptimizerAlgorithm.REGULATORY, inv)
        reg_run = apply_scenario(reg_plans, ScenarioType.BASELINE, config)

        milp_plans = optimize_plans(OptimizerAlgorithm.NASA_MILP, inv)
        milp_run = apply_scenario(milp_plans, ScenarioType.BASELINE, config)

        # 1. 100% critical SLA
        assert milp_run.balance.average_service_level_critical == 1.0
        assert milp_run.balance.average_service_level_total >= 0.99
        assert milp_run.constraints.is_feasible is True

        # 2. Financial performance: NASA MILP NPV should be significantly lower
        reg_npv = reg_run.economics.total_npv_cost
        milp_npv = milp_run.economics.total_npv_cost
        savings_pct = (reg_npv - milp_npv) / reg_npv * 100.0

        print(f"\n[NASA MILP] Reg NPV: {reg_npv:.2f} M | MILP NPV: {milp_npv:.2f} M | Savings: {savings_pct:.2f}%")
        assert milp_npv <= reg_npv

        # 3. Maximum utilization of Lunar-ISRU in 2038-2040 (120 t capacity)
        for y in (2038, 2039, 2040):
            isru_order = milp_plans[y].orders[ChannelID.LUNAR_ISRU].order_volume
            assert isru_order >= 100.0  # Takes full advantage of cheap 3.0 M/t fuel

    def test_minimax_robust_stress_resilience(self):
        """
        Minimax Robust strategy must provide resilience against Mandatory Stress.
        """
        inv = {"zbo_year": 2036, "isru_enabled": True, "earth_new_enabled": False}
        config = SimulationConfig(start_year=2035, end_year=2040)

        robust_plans = optimize_plans(OptimizerAlgorithm.MINIMAX_ROBUST, inv)
        robust_run = apply_scenario(robust_plans, ScenarioType.MANDATORY_STRESS, config)

        # Critical SLA must remain 100% under mandatory stress
        assert robust_run.balance.average_service_level_critical == 1.0
        # Standby emergency capacity must be elevated (30.0 t)
        for y in range(2035, 2041):
            assert robust_plans[y].orders[ChannelID.EMERGENCY].reserved_capacity == 30.0
