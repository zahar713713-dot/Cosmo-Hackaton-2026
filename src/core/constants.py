"""
Data structures, constants, and Pydantic v2 models for the Cis-lunar Fuel Depot planning.
Strict validation and zero-heuristics policy.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ChannelID(str, Enum):
    EARTH_CORE = "Earth-Core"
    EARTH_FLEX = "Earth-Flex"
    EARTH_NEW = "Earth-New"
    LUNAR_ISRU = "Lunar-ISRU"
    EMERGENCY = "Emergency"


# Simulation defaults
DEFAULT_START_YEAR: int = 2035
DEFAULT_END_YEAR: int = 2040
EXTENDED_MAX_YEAR: int = 2045
DAYS_IN_YEAR: int = 365
RESERVE_DAYS: int = 45

# Hard constraints
MIN_CRITICAL_SERVICE_LEVEL: float = 0.99
MIN_TOTAL_SERVICE_LEVEL: float = 0.97
MAX_CAPEX_2037: float = 1800.0
MAX_CAPEX_TOTAL: float = 2800.0
DEFAULT_DISCOUNT_RATE: float = 0.08  # Real annual discount rate r = 8%


class DemandRecord(BaseModel):
    """
    Annual propellant demand specification.
    Critical demand is strictly a subset of Total demand.
    """
    year: int = Field(..., ge=2030, le=2050, description="Planning year")
    base_total: float = Field(..., gt=0, description="Base total demand in tons/year")
    base_critical: float = Field(..., gt=0, description="Base critical demand in tons/year")
    low_total: Optional[float] = Field(None, gt=0, description="Low total demand scenario")
    high_total: Optional[float] = Field(None, gt=0, description="High total demand scenario")

    @model_validator(mode="after")
    def validate_critical_within_total(self) -> "DemandRecord":
        if self.base_critical > self.base_total:
            raise ValueError(
                f"Year {self.year}: Critical demand ({self.base_critical} t) cannot exceed "
                f"total demand ({self.base_total} t). Critical demand is a strict subset."
            )
        return self


class SupplyChannelConfig(BaseModel):
    """
    Parameters of a supply channel from Case Specifications.
    """
    channel_id: ChannelID
    name: str
    max_capacity: float = Field(..., gt=0, description="Maximum throughput capacity in tons/year")
    var_cost: float = Field(..., ge=0, description="Variable cost in million c.u./ton")
    res_tariff: float = Field(..., ge=0, description="Annual reservation tariff in million c.u. per ton/year reserved")
    take_or_pay: float = Field(..., ge=0.0, le=1.0, description="Take-or-pay fraction of reserved capacity (0.0 - 1.0)")
    lead_time_months: Optional[float] = Field(None, ge=0, description="Lead time in months")
    lead_time_weeks: Optional[float] = Field(None, ge=0, description="Lead time in weeks (Emergency)")
    annual_reliability: Dict[int, float] = Field(default_factory=dict, description="Nominal reliability metadata")


class StorageConfig(BaseModel):
    """
    Storage regime specifications.
    """
    name: str
    capacity_max: float = Field(..., gt=0, description="Storage tank maximum capacity in tons")
    throughput_loss_rate: float = Field(..., ge=0.0, le=1.0, description="Loss rate applied once on gross throughput")
    holding_cost_rate: float = Field(0.72, ge=0, description="Holding cost in million c.u./ton-year")
    additional_opex_annual: float = Field(0.0, ge=0, description="Additional fixed annual OPEX in million c.u./year")
    capex_required: float = Field(0.0, ge=0, description="One-time capital expenditure in million c.u.")
    min_available_year: int = Field(2035, ge=2030, description="Earliest available operational year")


# Standard Datasets from Case Rules
BASE_DEMAND: Dict[int, DemandRecord] = {
    2035: DemandRecord(year=2035, base_total=100.0, base_critical=80.0, low_total=80.0, high_total=110.0),
    2036: DemandRecord(year=2036, base_total=140.0, base_critical=105.0, low_total=112.0, high_total=154.0),
    2037: DemandRecord(year=2037, base_total=190.0, base_critical=135.0, low_total=152.0, high_total=209.0),
    2038: DemandRecord(year=2038, base_total=250.0, base_critical=170.0, low_total=200.0, high_total=312.5),
    2039: DemandRecord(year=2039, base_total=320.0, base_critical=210.0, low_total=256.0, high_total=400.0),
    2040: DemandRecord(year=2040, base_total=390.0, base_critical=250.0, low_total=312.0, high_total=487.5),
}

# Pre-populated extended demand projections (2041-2045) using transparent linear/exponential extrapolation
EXTENDED_DEMAND: Dict[int, DemandRecord] = {
    **BASE_DEMAND,
    2041: DemandRecord(year=2041, base_total=460.0, base_critical=295.0, low_total=368.0, high_total=575.0),
    2042: DemandRecord(year=2042, base_total=530.0, base_critical=340.0, low_total=424.0, high_total=662.5),
    2043: DemandRecord(year=2043, base_total=600.0, base_critical=385.0, low_total=480.0, high_total=750.0),
    2044: DemandRecord(year=2044, base_total=670.0, base_critical=430.0, low_total=536.0, high_total=837.5),
    2045: DemandRecord(year=2045, base_total=740.0, base_critical=475.0, low_total=592.0, high_total=925.0),
}

DEFAULT_CHANNELS: Dict[ChannelID, SupplyChannelConfig] = {
    ChannelID.EARTH_CORE: SupplyChannelConfig(
        channel_id=ChannelID.EARTH_CORE,
        name="Earth-Core",
        max_capacity=190.0,
        var_cost=6.2,
        res_tariff=0.45,
        take_or_pay=0.70,
        lead_time_months=12.0,
        annual_reliability={y: 0.96 for y in range(2035, 2046)},
    ),
    ChannelID.EARTH_FLEX: SupplyChannelConfig(
        channel_id=ChannelID.EARTH_FLEX,
        name="Earth-Flex",
        max_capacity=110.0,
        var_cost=8.9,
        res_tariff=0.15,
        take_or_pay=0.0,
        lead_time_months=4.0,
        annual_reliability={y: 0.985 for y in range(2035, 2046)},
    ),
    ChannelID.EARTH_NEW: SupplyChannelConfig(
        channel_id=ChannelID.EARTH_NEW,
        name="Earth-New",
        max_capacity=130.0,
        var_cost=7.1,
        res_tariff=0.30,
        take_or_pay=0.50,  # applies after commissioning
        lead_time_months=24.0,  # 18-24 months
        annual_reliability={2035: 0.88, 2036: 0.88, 2037: 0.88, 2038: 0.88, 2039: 0.94, 2040: 0.94},
    ),
    ChannelID.LUNAR_ISRU: SupplyChannelConfig(
        channel_id=ChannelID.LUNAR_ISRU,
        name="Lunar-ISRU",
        max_capacity=120.0,
        var_cost=3.0,
        res_tariff=0.0,
        take_or_pay=0.0,
        lead_time_months=2.0,  # 1-2 months after commissioning
        annual_reliability={2038: 0.78, 2039: 0.90, 2040: 0.93, 2041: 0.93, 2042: 0.93, 2043: 0.93, 2044: 0.93, 2045: 0.93},
    ),
    ChannelID.EMERGENCY: SupplyChannelConfig(
        channel_id=ChannelID.EMERGENCY,
        name="Emergency",
        max_capacity=80.0,
        var_cost=13.8,
        res_tariff=0.35,
        take_or_pay=0.0,
        lead_time_weeks=6.0,
        annual_reliability={y: 0.995 for y in range(2035, 2046)},
    ),
}

BASE_STORAGE = StorageConfig(
    name="Base Storage",
    capacity_max=70.0,
    throughput_loss_rate=0.045,  # 4.5%
    holding_cost_rate=0.72,
    additional_opex_annual=0.0,
    capex_required=0.0,
    min_available_year=2035,
)

ZBO_STORAGE = StorageConfig(
    name="ZBO Modernized Storage",
    capacity_max=120.0,
    throughput_loss_rate=0.012,  # 1.2%
    holding_cost_rate=0.72,
    additional_opex_annual=12.0,  # 12 M c.u./year
    capex_required=180.0,         # 180 M c.u.
    min_available_year=2036,
)


class ChannelOrder(BaseModel):
    """
    Operator decisions for a specific channel in a specific year.
    Strictly differentiates reservation and actual order volume.
    """
    channel_id: ChannelID
    reserved_capacity: float = Field(0.0, ge=0.0, description="Contracted capacity reservation (t/year)")
    order_volume: float = Field(0.0, ge=0.0, description="Volume ordered for actual delivery (t/year)")

    @model_validator(mode="after")
    def validate_order_within_reservation(self) -> "ChannelOrder":
        if self.order_volume > self.reserved_capacity + 1e-6:
            raise ValueError(
                f"Channel {self.channel_id.value}: Order volume ({self.order_volume:.2f} t) "
                f"cannot exceed reserved capacity ({self.reserved_capacity:.2f} t)."
            )
        return self


class YearlyPlan(BaseModel):
    """
    Complete annual decision package for the orbital fuel depot.
    """
    year: int = Field(..., ge=2035, le=2050)
    orders: Dict[ChannelID, ChannelOrder]
    zbo_invested: bool = Field(False, description="ZBO CAPEX committed in this or earlier years")
    isru_funded: bool = Field(False, description="Lunar-ISRU pilot CAPEX committed prior to 2038")
    isru_operational: bool = Field(False, description="Lunar-ISRU commissioned and producing fuel")
    earth_new_option_purchased: bool = Field(False, description="Earth-New option purchased (90 M c.u.)")
    earth_new_exercised: bool = Field(False, description="Earth-New option exercised (270 M c.u.)")
    earth_new_operational: bool = Field(False, description="Earth-New commissioned and available")


class SimulationConfig(BaseModel):
    """
    Global configuration for simulation execution.
    Allows horizon extension and custom discount rates.
    """
    start_year: int = Field(DEFAULT_START_YEAR, ge=2030, le=2040)
    end_year: int = Field(DEFAULT_END_YEAR, ge=2030, le=EXTENDED_MAX_YEAR)
    discount_rate: float = Field(DEFAULT_DISCOUNT_RATE, ge=0.0, le=0.5)
    initial_stock_2035: Optional[float] = Field(
        None, ge=0.0, description="Initial physical inventory at 2035-01-01. If None, set to 45-day requirement."
    )

    @model_validator(mode="after")
    def validate_horizon_order(self) -> "SimulationConfig":
        if self.end_year < self.start_year:
            raise ValueError(f"end_year ({self.end_year}) cannot be less than start_year ({self.start_year})")
        return self

    @property
    def horizon(self) -> List[int]:
        return list(range(self.start_year, self.end_year + 1))


DEFAULT_HORIZON: List[int] = list(range(DEFAULT_START_YEAR, DEFAULT_END_YEAR + 1))
