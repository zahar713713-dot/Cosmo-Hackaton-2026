"""
Economic and financial calculation engine for the orbital fuel depot.
Strictly implements the official rules:
- Variable payment: Var_Payment = Unit_Price * max(Order_Volume, TakeOrPay_Ratio * Reserved_Capacity)
- Reservation payment: Res_Payment = Res_Tariff * Reserved_Capacity
- Take-or-pay is NEVER charged a second time on top of minimum payment
- Storage cost: 0.72 * ((Start_Stock + End_Stock) / 2)
- Fixed OPEX for ZBO (12 M c.u./yr) and ISRU (70 M c.u./yr) once operational
- CAPEX tracking for ZBO (180), Earth-New (90 option + 270 execution = 360), Lunar-ISRU (1250)
- Net Present Cost (NPC / NPV of LCC) with annual discount rate r = 0.08
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import (
    ChannelID,
    SupplyChannelConfig,
    DEFAULT_CHANNELS,
    BASE_STORAGE,
    ZBO_STORAGE,
    DEFAULT_DISCOUNT_RATE,
    YearlyPlan,
    SimulationConfig,
)
from src.core.balance import SimulationBalanceResult


class ChannelCostBreakdown(BaseModel):
    """
    Cost breakdown for a single channel in a specific year.
    All values in million c.u.
    """
    channel_id: ChannelID
    reserved_capacity: float = Field(..., ge=0.0, description="Reserved capacity (t)")
    ordered_volume: float = Field(..., ge=0.0, description="Ordered volume (t)")
    delivered_volume: float = Field(..., ge=0.0, description="Physically delivered volume (t)")
    effective_unit_price: float = Field(..., ge=0.0, description="Scenario-adjusted unit price (M c.u./t)")
    reservation_tariff: float = Field(..., ge=0.0, description="Reservation tariff (M c.u./t)")
    take_or_pay_threshold: float = Field(..., ge=0.0, description="Minimum billable volume (t)")
    billable_volume: float = Field(..., ge=0.0, description="max(ordered_volume, take_or_pay_threshold)")
    
    reservation_payment: float = Field(..., ge=0.0, description="Reservation fee = tariff * reserved")
    variable_payment: float = Field(..., ge=0.0, description="Variable fee = price * billable_volume")
    total_channel_payment: float = Field(..., ge=0.0, description="Sum of reservation + variable payment")


class YearlyEconomicsResult(BaseModel):
    """
    Financial summary for a single calendar year (million c.u. in 2035 constant terms).
    """
    year: int
    channel_costs: Dict[ChannelID, ChannelCostBreakdown]
    
    # OPEX categories
    procurement_cost: float = Field(..., ge=0.0, description="Sum of all channel variable payments")
    reservation_cost: float = Field(..., ge=0.0, description="Sum of all channel reservation fees")
    storage_holding_cost: float = Field(..., ge=0.0, description="Average stock * 0.72")
    zbo_fixed_opex: float = Field(0.0, ge=0.0, description="ZBO annual operational expense (12 M c.u.)")
    isru_fixed_opex: float = Field(0.0, ge=0.0, description="Lunar-ISRU annual operational expense (70 M c.u.)")
    initial_stock_acquisition_cost: float = Field(
        0.0, ge=0.0, description="Pre-start procurement cost for 2035 initial stock (charged in 2035)"
    )
    total_opex: float = Field(..., ge=0.0, description="Total operational expenditure in year t")
    
    # CAPEX categories
    capex_zbo: float = Field(0.0, ge=0.0, description="ZBO upgrade CAPEX (180 M c.u.)")
    capex_earth_new: float = Field(0.0, ge=0.0, description="Earth-New option and execution CAPEX (90/270 M c.u.)")
    capex_isru: float = Field(0.0, ge=0.0, description="Lunar-ISRU pilot CAPEX (1250 M c.u.)")
    total_capex: float = Field(..., ge=0.0, description="Total capital expenditure in year t")
    
    total_expenditure: float = Field(..., ge=0.0, description="OPEX + CAPEX in year t")
    discount_factor: float = Field(..., gt=0.0, description="1 / (1 + r)^(t - 2035)")
    discounted_expenditure: float = Field(..., ge=0.0, description="total_expenditure * discount_factor")


class SimulationEconomicsResult(BaseModel):
    """
    Complete financial results over the planning horizon.
    """
    yearly_economics: Dict[int, YearlyEconomicsResult]
    total_procurement_cost: float = Field(..., ge=0.0)
    total_reservation_cost: float = Field(..., ge=0.0)
    total_storage_cost: float = Field(..., ge=0.0)
    total_fixed_opex: float = Field(..., ge=0.0)
    total_opex: float = Field(..., ge=0.0)
    total_capex: float = Field(..., ge=0.0)
    total_undiscounted_cost: float = Field(..., ge=0.0)
    total_npv_cost: float = Field(..., ge=0.0, description="Net Present Cost / discounted Life Cycle Cost")
    cost_per_ton_delivered: float = Field(..., ge=0.0, description="Total undiscounted cost / total delivered fuel")
    cost_per_ton_served: float = Field(..., ge=0.0, description="Total undiscounted cost / total served demand")
    discounted_cost_per_ton_served: float = Field(..., ge=0.0, description="NPV Cost / total served demand")


def calculate_economics(
    plans: Dict[int, YearlyPlan],
    balance_results: SimulationBalanceResult,
    config: SimulationConfig,
    channels: Optional[Dict[ChannelID, SupplyChannelConfig]] = None,
    price_multipliers: Optional[Dict[int, Dict[ChannelID, float]]] = None,
    capex_schedule_override: Optional[Dict[int, Dict[str, float]]] = None,
) -> SimulationEconomicsResult:
    """
    Calculates procurement, reservation, holding, fixed OPEX, CAPEX, and LCC (NPV).
    """
    if channels is None:
        channels = DEFAULT_CHANNELS
    
    r = config.discount_rate
    start_year = config.start_year
    yearly_econ: Dict[int, YearlyEconomicsResult] = {}

    tot_proc = 0.0
    tot_res = 0.0
    tot_storage = 0.0
    tot_fixed = 0.0
    tot_opex = 0.0
    tot_capex = 0.0
    tot_undisc = 0.0
    tot_npv = 0.0

    # Track prior investments to avoid double-charging CAPEX
    zbo_charged = False
    earth_new_opt_charged = False
    earth_new_exec_charged = False
    isru_charged = False

    for year in config.horizon:
        plan = plans[year]
        bal = balance_results.yearly_results[year]
        t_delta = year - start_year
        discount_factor = 1.0 / ((1.0 + r) ** t_delta)

        channel_costs: Dict[ChannelID, ChannelCostBreakdown] = {}
        year_procurement = 0.0
        year_reservation = 0.0

        for ch_id, ch_cfg in channels.items():
            order = plan.orders.get(ch_id)
            reserved_cap = order.reserved_capacity if order else 0.0
            order_vol = order.order_volume if order else 0.0
            deliv_vol = bal.channel_deliveries.get(ch_id, 0.0)

            # Scenario price adjustment
            mult = 1.0
            if price_multipliers and year in price_multipliers:
                mult = price_multipliers[year].get(ch_id, 1.0)
            
            eff_unit_price = ch_cfg.var_cost * mult
            res_tariff = ch_cfg.res_tariff

            # Take-or-pay rule
            # For Earth-New, take-or-pay applies after commissioning
            top_ratio = ch_cfg.take_or_pay
            if ch_id == ChannelID.EARTH_NEW and not plan.earth_new_operational:
                top_ratio = 0.0

            top_threshold = top_ratio * reserved_cap
            billable_volume = max(order_vol, top_threshold)

            # Payments
            res_payment = res_tariff * reserved_cap
            var_payment = eff_unit_price * billable_volume
            tot_channel = res_payment + var_payment

            channel_costs[ch_id] = ChannelCostBreakdown(
                channel_id=ch_id,
                reserved_capacity=round(reserved_cap, 4),
                ordered_volume=round(order_vol, 4),
                delivered_volume=round(deliv_vol, 4),
                effective_unit_price=round(eff_unit_price, 4),
                reservation_tariff=round(res_tariff, 4),
                take_or_pay_threshold=round(top_threshold, 4),
                billable_volume=round(billable_volume, 4),
                reservation_payment=round(res_payment, 4),
                variable_payment=round(var_payment, 4),
                total_channel_payment=round(tot_channel, 4),
            )

            year_procurement += var_payment
            year_reservation += res_payment

        # Holding cost: 0.72 * ((start_stock + end_stock) / 2)
        avg_inventory = (bal.start_stock + bal.end_stock) / 2.0
        storage_cost = 0.72 * avg_inventory

        # Fixed OPEX
        zbo_opex = 12.0 if (plan.zbo_invested and year >= ZBO_STORAGE.min_available_year) else 0.0
        isru_opex = 70.0 if (plan.isru_operational and year >= 2038) else 0.0

        # Initial stock 2035 acquisition cost:
        # Pre-start purchase charged in year 1 at Earth-Core base price
        init_stock_cost = 0.0
        if year == start_year:
            # Procured at Earth-Core tariff (6.2 + 0.45 = 6.65 M c.u./t)
            init_stock_cost = bal.start_stock * (DEFAULT_CHANNELS[ChannelID.EARTH_CORE].var_cost + 
                                                  DEFAULT_CHANNELS[ChannelID.EARTH_CORE].res_tariff)

        year_opex = year_procurement + year_reservation + storage_cost + zbo_opex + isru_opex + init_stock_cost

        # CAPEX handling
        c_zbo = 0.0
        c_en = 0.0
        c_isru = 0.0

        if capex_schedule_override and year in capex_schedule_override:
            c_zbo = capex_schedule_override[year].get("zbo", 0.0)
            c_en = capex_schedule_override[year].get("earth_new", 0.0)
            c_isru = capex_schedule_override[year].get("isru", 0.0)
        else:
            # ZBO: 180 M c.u. when first invested (earliest 2036)
            if plan.zbo_invested and not zbo_charged and year >= 2036:
                c_zbo = ZBO_STORAGE.capex_required
                zbo_charged = True

            # Earth-New: 90 option + 270 execution
            if plan.earth_new_option_purchased and not earth_new_opt_charged:
                c_en += 90.0
                earth_new_opt_charged = True
            if plan.earth_new_exercised and not earth_new_exec_charged:
                c_en += 270.0
                earth_new_exec_charged = True

            # Lunar-ISRU: 1250 M c.u. funded prior to 2038
            if plan.isru_funded and not isru_charged:
                c_isru = 1250.0
                isru_charged = True

        year_capex = c_zbo + c_en + c_isru
        year_total = year_opex + year_capex
        year_npv = year_total * discount_factor

        yearly_econ[year] = YearlyEconomicsResult(
            year=year,
            channel_costs=channel_costs,
            procurement_cost=round(year_procurement, 4),
            reservation_cost=round(year_reservation, 4),
            storage_holding_cost=round(storage_cost, 4),
            zbo_fixed_opex=round(zbo_opex, 4),
            isru_fixed_opex=round(isru_opex, 4),
            initial_stock_acquisition_cost=round(init_stock_cost, 4),
            total_opex=round(year_opex, 4),
            capex_zbo=round(c_zbo, 4),
            capex_earth_new=round(c_en, 4),
            capex_isru=round(c_isru, 4),
            total_capex=round(year_capex, 4),
            total_expenditure=round(year_total, 4),
            discount_factor=round(discount_factor, 6),
            discounted_expenditure=round(year_npv, 4),
        )

        tot_proc += year_procurement
        tot_res += year_reservation
        tot_storage += storage_cost
        tot_fixed += (zbo_opex + isru_opex)
        tot_opex += year_opex
        tot_capex += year_capex
        tot_undisc += year_total
        tot_npv += year_npv

    tot_served = balance_results.total_served_demand
    tot_delivered = balance_results.total_gross_delivery

    cost_per_ton_deliv = tot_undisc / tot_delivered if tot_delivered > 0 else 0.0
    cost_per_ton_srv = tot_undisc / tot_served if tot_served > 0 else 0.0
    disc_cost_per_ton_srv = tot_npv / tot_served if tot_served > 0 else 0.0

    return SimulationEconomicsResult(
        yearly_economics=yearly_econ,
        total_procurement_cost=round(tot_proc, 4),
        total_reservation_cost=round(tot_res, 4),
        total_storage_cost=round(tot_storage, 4),
        total_fixed_opex=round(tot_fixed, 4),
        total_opex=round(tot_opex, 4),
        total_capex=round(tot_capex, 4),
        total_undiscounted_cost=round(tot_undisc, 4),
        total_npv_cost=round(tot_npv, 4),
        cost_per_ton_delivered=round(cost_per_ton_deliv, 4),
        cost_per_ton_served=round(cost_per_ton_srv, 4),
        discounted_cost_per_ton_served=round(disc_cost_per_ton_srv, 4),
    )
