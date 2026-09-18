"""
Precision verification tests for physical material balance and storage arithmetic.
Verifies Criteria 1 & 5 (Model correctness and reproducibility).
"""

import pytest
from src.core.constants import (
    ChannelID,
    DemandRecord,
    SimulationConfig,
    YearlyPlan,
    ChannelOrder,
    BASE_DEMAND,
    DEFAULT_CHANNELS,
)
from src.core.balance import calculate_material_balance
from src.core.economics import calculate_economics


class TestBalanceVerification:
    def test_2035_official_benchmark_example(self):
        """
        Official Case Benchmark calculation for 2035:
        - Opening inventory: 100 * 45 / 365 = 12.3288 t (rounded to 4 decimal places)
        - Earth-Core Order: 95.0000 t
        - Base Storage Throughput Loss Rate: 4.5%
        - Losses = 95.0 * 0.045 = 4.2750 t
        - Net Inflow = 95.0 - 4.275 = 90.7250 t
        - Total Fuel Available = 12.3288 + 90.7250 = 103.0538 t
        - Demand Total = 100.0000 t (Critical = 80.0000 t)
        - Served Total = 100.0000 t (Critical served = 80.0000 t, 100% coverage)
        - Deficit = 0.0000 t
        - Ending Stock = 12.3288 + 95.0000 - 4.2750 - 100.0000 = 3.0538 t
        """
        init_stock = 100.0 * 45.0 / 365.0  # 12.328767...
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=init_stock)
        
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE,
                        reserved_capacity=95.0,
                        order_volume=95.0,
                    ),
                    ChannelID.EARTH_FLEX: ChannelOrder(
                        channel_id=ChannelID.EARTH_FLEX, reserved_capacity=0.0, order_volume=0.0
                    ),
                    ChannelID.EARTH_NEW: ChannelOrder(
                        channel_id=ChannelID.EARTH_NEW, reserved_capacity=0.0, order_volume=0.0
                    ),
                    ChannelID.LUNAR_ISRU: ChannelOrder(
                        channel_id=ChannelID.LUNAR_ISRU, reserved_capacity=0.0, order_volume=0.0
                    ),
                    ChannelID.EMERGENCY: ChannelOrder(
                        channel_id=ChannelID.EMERGENCY, reserved_capacity=0.0, order_volume=0.0
                    ),
                },
                zbo_invested=False,
            )
        }

        demand = {2035: DemandRecord(year=2035, base_total=100.0, base_critical=80.0)}
        res = calculate_material_balance(plans, demand, config)
        y_res = res.yearly_results[2035]

        # Verify all numbers to 4 decimal places
        assert round(y_res.start_stock, 4) == 12.3288
        assert round(y_res.gross_delivery, 4) == 95.0000
        assert round(y_res.losses, 4) == 4.2750
        assert round(y_res.net_available_inflow, 4) == 90.7250
        assert round(y_res.total_fuel_available, 4) == 103.0538
        assert round(y_res.served_demand_total, 4) == 100.0000
        assert round(y_res.served_demand_critical, 4) == 80.0000
        assert round(y_res.deficit_total, 4) == 0.0000
        assert round(y_res.deficit_critical, 4) == 0.0000
        assert round(y_res.end_stock, 4) == 3.0538
        assert y_res.service_level_total == 1.0
        assert y_res.service_level_critical == 1.0

    def test_non_negative_inventory_and_deficit_isolation(self):
        """
        When demand exceeds available propellant:
        - End stock MUST be strictly 0.0 (cannot become negative)
        - Shortage must be recorded quantitatively as a distinct metric
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
        # Demand = 150 (Total), 100 (Crit)
        # Gross delivery = 50, Losses = 50 * 0.045 = 2.25, Net = 47.75
        # Total Available = 10.0 + 47.75 = 57.75
        # Served = 57.75 (Critical served = 57.75, Critical deficit = 42.25)
        # Total Deficit = 150 - 57.75 = 92.25
        # End stock = 0.0 (NOT -92.25)
        demand = {2035: DemandRecord(year=2035, base_total=150.0, base_critical=100.0)}
        res = calculate_material_balance(plans, demand, config)
        y_res = res.yearly_results[2035]

        assert y_res.end_stock == 0.0
        assert y_res.end_stock >= 0.0
        assert abs(y_res.served_demand_total - 57.75) < 1e-4
        assert abs(y_res.served_demand_critical - 57.75) < 1e-4
        assert abs(y_res.deficit_total - 92.25) < 1e-4
        assert abs(y_res.deficit_critical - 42.25) < 1e-4

    def test_losses_on_throughput_and_holding_cost_on_average_inventory(self):
        """
        Rule validation:
        1. Losses are charged ONCE on gross delivery (throughput), not on inventory.
        2. Holding cost is calculated strictly on average physical inventory:
           Storage_Cost = 0.72 * ((Start_Stock + End_Stock) / 2)
        """
        start_stock = 20.0
        order_vol = 100.0
        # Gross = 100, Losses = 100 * 0.045 = 4.5, Net = 95.5
        # Available = 20 + 95.5 = 115.5
        # Demand = 80 -> Served = 80
        # End stock = 115.5 - 80 = 35.5
        # Average inventory = (20 + 35.5) / 2 = 27.75
        # Holding cost = 0.72 * 27.75 = 19.98 M c.u.
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=start_stock)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=order_vol, order_volume=order_vol
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=80.0, base_critical=60.0)}
        bal_res = calculate_material_balance(plans, demand, config)
        econ_res = calculate_economics(plans, bal_res, config)

        y_bal = bal_res.yearly_results[2035]
        y_econ = econ_res.yearly_economics[2035]

        # Verify losses once on throughput
        assert abs(y_bal.losses - 4.5) < 1e-4
        assert abs(y_bal.end_stock - 35.5) < 1e-4

        # Verify holding cost
        expected_avg_stock = (20.0 + 35.5) / 2.0
        expected_holding_cost = 0.72 * expected_avg_stock
        assert abs(y_econ.storage_holding_cost - expected_holding_cost) < 1e-4
        assert abs(y_econ.storage_holding_cost - 19.98) < 1e-4

    def test_take_or_pay_enforcement(self):
        """
        Channel A (Earth-Core) Take-or-pay rule:
        Reserved Capacity = 100 t/year.
        Take-or-pay ratio = 70% -> Minimum billable volume = 70 t.
        If order is 40 t (< 70 t):
        Variable payment = 70 t * 6.2 M c.u./t = 434.0 M c.u.
        Reservation payment = 100 t * 0.45 M c.u./t = 45.0 M c.u.
        Total = 479.0 M c.u.
        """
        config = SimulationConfig(start_year=2035, end_year=2035, initial_stock_2035=10.0)
        plans = {
            2035: YearlyPlan(
                year=2035,
                orders={
                    ChannelID.EARTH_CORE: ChannelOrder(
                        channel_id=ChannelID.EARTH_CORE, reserved_capacity=100.0, order_volume=40.0
                    )
                },
                zbo_invested=False,
            )
        }
        demand = {2035: DemandRecord(year=2035, base_total=40.0, base_critical=30.0)}
        bal_res = calculate_material_balance(plans, demand, config)
        econ_res = calculate_economics(plans, bal_res, config)

        core_cost = econ_res.yearly_economics[2035].channel_costs[ChannelID.EARTH_CORE]
        assert core_cost.take_or_pay_threshold == 70.0
        assert core_cost.billable_volume == 70.0
        assert abs(core_cost.variable_payment - 434.0) < 1e-4
        assert abs(core_cost.reservation_payment - 45.0) < 1e-4
        assert abs(core_cost.total_channel_payment - 479.0) < 1e-4
