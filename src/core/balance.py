"""
Physical material balance engine for the orbital fuel depot.
Strictly implements the official case rules:
- Losses are charged ONCE on gross throughput: Losses = Gross_Delivery * loss_rate
- Physical inventory is strictly non-negative: Stock >= 0
- Deficit is tracked as a separate metric: Shortage = Demand - Served
- Critical demand is served with priority as a subset of total demand.
- 45-day reserve threshold: R = Demand_Total * 45 / 365
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.core.constants import (
    ChannelID,
    DemandRecord,
    StorageConfig,
    BASE_STORAGE,
    ZBO_STORAGE,
    DAYS_IN_YEAR,
    RESERVE_DAYS,
    YearlyPlan,
    SimulationConfig,
)


class YearlyBalanceResult(BaseModel):
    """
    Physical balance results for a single calendar year.
    All quantities in metric tons (t).
    """
    year: int
    start_stock: float = Field(..., ge=0.0, description="Physical inventory at the start of the year (t)")
    gross_delivery: float = Field(..., ge=0.0, description="Gross fuel delivered across all channels (t)")
    channel_deliveries: Dict[ChannelID, float] = Field(default_factory=dict, description="Fuel delivered by channel (t)")
    throughput_loss_rate: float = Field(..., ge=0.0, le=1.0, description="Loss rate applied to gross delivery")
    losses: float = Field(..., ge=0.0, description="Handling and evaporation losses (t)")
    net_available_inflow: float = Field(..., ge=0.0, description="Gross delivery minus losses (t)")
    total_fuel_available: float = Field(..., ge=0.0, description="Start stock + net available inflow (t)")
    
    # Demand and service
    demand_total: float = Field(..., gt=0.0, description="Total annual demand (t)")
    demand_critical: float = Field(..., gt=0.0, description="Critical subset demand (t)")
    served_demand_total: float = Field(..., ge=0.0, description="Actually delivered fuel to missions (t)")
    served_demand_critical: float = Field(..., ge=0.0, description="Delivered to critical missions (t)")
    served_demand_other: float = Field(..., ge=0.0, description="Delivered to non-critical missions (t)")
    
    # Shortages
    deficit_total: float = Field(..., ge=0.0, description="Unserved total demand (t)")
    deficit_critical: float = Field(..., ge=0.0, description="Unserved critical demand (t)")
    
    # End inventory & limits
    end_stock: float = Field(..., ge=0.0, description="Closing inventory at year end (t)")
    storage_capacity_max: float = Field(..., gt=0.0, description="Current depot tank capacity (t)")
    is_storage_overflow: bool = Field(False, description="True if peak/end inventory exceeds tank capacity")
    overflow_amount: float = Field(0.0, ge=0.0, description="Volume exceeding tank capacity (t)")
    
    # 45-day reserve check
    required_reserve_45d: float = Field(..., ge=0.0, description="Mandatory 45-day reserve threshold (t)")
    is_reserve_satisfied_physically: bool = Field(..., description="True if start_stock >= required_reserve_45d")
    physical_reserve_deficit: float = Field(0.0, ge=0.0, description="Gap in physical reserve if below 45d (t)")
    
    # Service levels
    service_level_total: float = Field(..., ge=0.0, le=1.0, description="Ratio of served total to total demand")
    service_level_critical: float = Field(..., ge=0.0, le=1.0, description="Ratio of served critical to critical demand")


class SimulationBalanceResult(BaseModel):
    """
    Complete balance trajectory over the planning horizon.
    """
    yearly_results: Dict[int, YearlyBalanceResult]
    total_gross_delivery: float = Field(..., ge=0.0)
    total_losses: float = Field(..., ge=0.0)
    total_served_demand: float = Field(..., ge=0.0)
    total_deficit: float = Field(..., ge=0.0)
    average_service_level_total: float = Field(..., ge=0.0, le=1.0)
    average_service_level_critical: float = Field(..., ge=0.0, le=1.0)


def calculate_material_balance(
    plans: Dict[int, YearlyPlan],
    demand: Dict[int, DemandRecord],
    config: SimulationConfig,
    actual_delivery_multipliers: Optional[Dict[int, Dict[ChannelID, float]]] = None,
    storage_override: Optional[Dict[int, StorageConfig]] = None,
) -> SimulationBalanceResult:
    """
    Executes sequential physical material balance for all years in the horizon.
    
    Args:
        plans: Dictionary of annual plans by year.
        demand: Dictionary of demand records by year.
        config: Simulation configuration (horizon, discount rate, initial stock).
        actual_delivery_multipliers: Sourced from scenario (e.g. Lunar-ISRU 55% in 2038).
        storage_override: Optional custom storage specifications by year.
    """
    yearly_results: Dict[int, YearlyBalanceResult] = {}
    
    # Initial physical stock at 2035-01-01
    start_year = config.start_year
    first_year_demand = demand[start_year].base_total
    
    if config.initial_stock_2035 is not None:
        current_stock = config.initial_stock_2035
    else:
        # Default: exactly satisfies 45-day requirement: 100 * 45 / 365 = ~12.33 tons
        current_stock = first_year_demand * (RESERVE_DAYS / DAYS_IN_YEAR)

    total_gross = 0.0
    total_losses = 0.0
    total_served = 0.0
    total_deficit = 0.0

    for year in config.horizon:
        plan = plans[year]
        d_record = demand[year]
        demand_total = d_record.base_total
        demand_crit = d_record.base_critical
        
        # Determine active storage configuration (Base vs ZBO)
        if storage_override and year in storage_override:
            current_storage = storage_override[year]
        else:
            # ZBO is active if invested in this or earlier years (earliest allowed 2036)
            is_zbo = plan.zbo_invested and (year >= ZBO_STORAGE.min_available_year)
            current_storage = ZBO_STORAGE if is_zbo else BASE_STORAGE
        
        # Calculate delivered fuel per channel taking into account scenario delivery multipliers
        channel_deliveries: Dict[ChannelID, float] = {}
        gross_delivery = 0.0
        
        for ch_id, order in plan.orders.items():
            mult = 1.0
            if actual_delivery_multipliers and year in actual_delivery_multipliers:
                mult = actual_delivery_multipliers[year].get(ch_id, 1.0)
            
            delivered_k = order.order_volume * mult
            channel_deliveries[ch_id] = delivered_k
            gross_delivery += delivered_k

        # Rule 1: Losses are charged ONCE on gross throughput
        loss_rate = current_storage.throughput_loss_rate
        losses = gross_delivery * loss_rate
        net_inflow = gross_delivery - losses
        
        # Total fuel available to serve demand this year
        available_fuel = current_stock + net_inflow
        
        # Rule 2: Service and Deficit (inventory cannot go negative)
        served_total = min(available_fuel, demand_total)
        deficit_total = demand_total - served_total
        
        # Critical demand served with priority
        served_critical = min(served_total, demand_crit)
        deficit_critical = demand_crit - served_critical
        served_other = served_total - served_critical
        
        # Rule 3: Closing inventory formula: End_Stock = Start_Stock + Gross_Delivery - Losses - Served
        end_stock = available_fuel - served_total
        # Numerical guard against tiny floating-point negatives
        end_stock = max(0.0, end_stock)

        # Rule 4: Storage tank overflow validation
        capacity_max = current_storage.capacity_max
        is_overflow = end_stock > capacity_max + 1e-6
        overflow_amount = max(0.0, end_stock - capacity_max)

        # Rule 5: 45-day reserve threshold on start_stock
        required_reserve = demand_total * (RESERVE_DAYS / DAYS_IN_YEAR)
        is_reserve_met = current_stock >= (required_reserve - 1e-6)
        reserve_gap = max(0.0, required_reserve - current_stock)

        # Service level calculations
        sl_total = served_total / demand_total if demand_total > 0 else 1.0
        sl_critical = served_critical / demand_crit if demand_crit > 0 else 1.0

        yearly_res = YearlyBalanceResult(
            year=year,
            start_stock=round(current_stock, 4),
            gross_delivery=round(gross_delivery, 4),
            channel_deliveries={k: round(v, 4) for k, v in channel_deliveries.items()},
            throughput_loss_rate=loss_rate,
            losses=round(losses, 4),
            net_available_inflow=round(net_inflow, 4),
            total_fuel_available=round(available_fuel, 4),
            demand_total=round(demand_total, 4),
            demand_critical=round(demand_crit, 4),
            served_demand_total=round(served_total, 4),
            served_demand_critical=round(served_critical, 4),
            served_demand_other=round(served_other, 4),
            deficit_total=round(deficit_total, 4),
            deficit_critical=round(deficit_critical, 4),
            end_stock=round(end_stock, 4),
            storage_capacity_max=capacity_max,
            is_storage_overflow=is_overflow,
            overflow_amount=round(overflow_amount, 4),
            required_reserve_45d=round(required_reserve, 4),
            is_reserve_satisfied_physically=is_reserve_met,
            physical_reserve_deficit=round(reserve_gap, 4),
            service_level_total=round(sl_total, 6),
            service_level_critical=round(sl_critical, 6),
        )

        yearly_results[year] = yearly_res

        total_gross += gross_delivery
        total_losses += losses
        total_served += served_total
        total_deficit += deficit_total

        # Roll over stock to next year
        current_stock = end_stock

    years_count = len(config.horizon)
    avg_sl_total = sum(r.service_level_total for r in yearly_results.values()) / years_count
    avg_sl_crit = sum(r.service_level_critical for r in yearly_results.values()) / years_count

    return SimulationBalanceResult(
        yearly_results=yearly_results,
        total_gross_delivery=round(total_gross, 4),
        total_losses=round(total_losses, 4),
        total_served_demand=round(total_served, 4),
        total_deficit=round(total_deficit, 4),
        average_service_level_total=round(avg_sl_total, 6),
        average_service_level_critical=round(avg_sl_crit, 6),
    )
