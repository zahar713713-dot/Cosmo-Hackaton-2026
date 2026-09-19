"""
Pydantic v2 schemas for request validation and structured API responses.
Enforces strict range validation and provides friendly Russian diagnostic error messages.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from src.core.constants import (
    ChannelID,
    DEFAULT_DISCOUNT_RATE,
    BASE_DEMAND,
    DEFAULT_CHANNELS,
    StorageConfig,
    BASE_STORAGE,
    ZBO_STORAGE,
)


class ChannelPlanInput(BaseModel):
    """
    Operator's decisions for a single channel in a single year.
    """
    reserved_capacity: float = Field(..., ge=0.0, description="Зарезервированная мощность (т/год)")
    target_order_volume: float = Field(..., ge=0.0, description="Плановый отбор топлива (т/год)")

    @model_validator(mode="after")
    def check_order_within_reservation(self) -> "ChannelPlanInput":
        if self.target_order_volume > self.reserved_capacity + 1e-5:
            raise ValueError(
                f"Объём заказа ({self.target_order_volume:.2f} т) не может превышать "
                f"зарезервированную мощность ({self.reserved_capacity:.2f} т)."
            )
        return self


class InvestmentsInput(BaseModel):
    """
    Operator's strategic investment decisions.
    """
    zbo_year: Optional[int] = Field(
        2036, ge=2036, le=2045, description="Год инвестиции в ZBO-модернизацию (не ранее 2036 г.)"
    )
    isru_enabled: bool = Field(True, description="Флаг ввода лунного источника Lunar-ISRU")
    isru_capex_schedule: Optional[Dict[int, float]] = Field(
        default_factory=lambda: {2035: 250.0, 2036: 500.0, 2037: 500.0},
        description="График финансирования CAPEX ISRU (1250 млн у.е. строго до 2038 г.)",
    )
    earth_new_enabled: bool = Field(False, description="Флаг использования канала Earth-New")
    earth_new_option_year: Optional[int] = Field(None, ge=2035, le=2045, description="Год покупки опциона (90 млн у.е.)")
    earth_new_exercise_year: Optional[int] = Field(None, ge=2035, le=2045, description="Год исполнения опциона (270 млн у.е.)")


class CustomParamsInput(BaseModel):
    """
    Custom overrides for sensitivity testing and stress exploration.
    """
    price_multipliers: Optional[Dict[int, Dict[ChannelID, float]]] = Field(
        None, description="Множители цен по годам и каналам"
    )
    demand_total_multipliers: Optional[Dict[int, float]] = Field(
        None, description="Сценарные множители к общему спросу"
    )
    loss_rate_override: Optional[float] = Field(
        None, ge=0.0, le=0.20, description="Переопределение потерь хранилища"
    )


class SimulationRequest(BaseModel):
    """
    Main payload for simulation execution.
    """
    scenario_type: str = Field(
        "baseline",
        description="Тип сценария: 'baseline', 'stress', 'high_demand', 'low_demand', 'custom', 'geopolitical'",
    )
    investments: InvestmentsInput = Field(default_factory=InvestmentsInput)
    channel_plans: Dict[int, Dict[ChannelID, ChannelPlanInput]] = Field(
        ..., description="Планы бронирования и отбора по годам (2035–2040)"
    )
    custom_params: Optional[CustomParamsInput] = None
    discount_rate: float = Field(DEFAULT_DISCOUNT_RATE, ge=0.0, le=0.5, description="Ставка дисконтирования r")
    initial_stock_2035: Optional[float] = Field(
        None, ge=0.0, description="Начальный запас на 2035 год (если не задан, 45 дней спроса)"
    )

    @field_validator("scenario_type")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        allowed = {"baseline", "stress", "high_demand", "low_demand", "custom", "geopolitical"}
        v_clean = v.lower().strip()
        if v_clean not in allowed:
            raise ValueError(f"Недопустимый тип сценария '{v}'. Допустимы: {allowed}")
        return v_clean


class YearlyBalanceDTO(BaseModel):
    year: int
    start_stock: float
    gross_delivery: float
    losses: float
    net_available_inflow: float
    total_fuel_available: float
    demand_total: float
    demand_critical: float
    served_demand_total: float
    served_demand_critical: float
    deficit_total: float
    deficit_critical: float
    end_stock: float
    storage_capacity_max: float
    is_storage_overflow: bool
    overflow_amount: float
    required_reserve_45d: float
    is_reserve_satisfied: bool
    service_level_total: float
    service_level_critical: float
    channel_deliveries: Dict[str, float]
    emergency_reserve: float = 0.0
    guaranteed_buffer_total: float = 0.0


class YearlyEconomicsDTO(BaseModel):
    year: int
    procurement_cost: float
    reservation_cost: float
    storage_holding_cost: float
    zbo_fixed_opex: float
    isru_fixed_opex: float
    initial_stock_acquisition_cost: float
    total_opex: float
    capex_zbo: float
    capex_earth_new: float
    capex_isru: float
    total_capex: float
    total_expenditure: float
    discount_factor: float
    discounted_expenditure: float
    channel_payments: Dict[str, float]


class ViolationDTO(BaseModel):
    year: str
    rule_code: str
    rule_name: str
    expected: str
    actual: str
    message: str
    is_violated: bool


class SimulationResponse(BaseModel):
    scenario_type: str
    scenario_name: str
    is_feasible: bool
    summary_kpi: Dict[str, Any]
    yearly_balance: List[YearlyBalanceDTO]
    yearly_economics: List[YearlyEconomicsDTO]
    violations: List[ViolationDTO]


class CompareRequest(BaseModel):
    """
    Payload for multi-scenario comparative evaluation.
    """
    scenarios: List[SimulationRequest] = Field(..., min_length=2, max_length=5)
    labels: Optional[List[str]] = Field(None, description="Пользовательские подписи к сценариям")


class CompareResponse(BaseModel):
    summary_matrix: List[Dict[str, Any]]
    deltas_vs_first: List[Dict[str, Any]]


class SensitivityRequest(BaseModel):
    """
    Payload for sensitivity / Tornado analysis.
    """
    base_request: SimulationRequest
    price_shock_range: List[float] = Field(
        default_factory=lambda: [-0.20, -0.10, 0.0, 0.10, 0.20, 0.30, 0.40],
        description="Сетка отклонений переменных цен земных каналов",
    )
    demand_shock_range: List[float] = Field(
        default_factory=lambda: [-0.20, -0.10, 0.0, 0.10, 0.20],
        description="Сетка отклонений общего спроса",
    )
    isru_delay_years: List[int] = Field(
        default_factory=lambda: [0, 1, 2],
        description="Задержка ввода Lunar-ISRU на N лет",
    )


class SensitivityPoint(BaseModel):
    parameter: str
    variation: str
    total_cost: float
    npv_cost: float
    total_deficit: float
    min_service_level: float
    is_feasible: bool


class SensitivityResponse(BaseModel):
    tornado_points: List[SensitivityPoint]
    cost_elasticities: Dict[str, float]
    critical_thresholds: List[str]


class GeopoliticalShockRequest(BaseModel):
    """
    Payload for bonus geopolitical shock evaluation (+5 points).
    """
    base_request: SimulationRequest
    start_year: int = Field(2037, ge=2035, le=2045)
    end_year: int = Field(2039, ge=2035, le=2045)
    earth_core_price_multiplier: float = Field(1.35, ge=0.5, le=3.0, description="Надбавка к тарифу Earth-Core")
    earth_flex_price_multiplier: float = Field(1.40, ge=0.5, le=3.0, description="Надбавка к тарифу Earth-Flex")
    earth_core_capacity_cap: Optional[float] = Field(None, gt=0.0, description="Санкционный лимит пусков (т/год)")
    description: str = Field(
        "Геополитическое эмбарго на запуски и скачок страховых премий доставки КРТ.",
        description="Описание сценарного события",
    )


class GeopoliticalShockResponse(BaseModel):
    simulation_result: SimulationResponse
    cost_delta_vs_baseline: float
    npv_delta_vs_baseline: float
    service_delta_vs_baseline: float
    narrative_impact: str


class OptimizerAlgorithmDTO(BaseModel):
    id: str
    name: str
    short_name: str
    foundation: str
    description: str
    target_metric: str
    badge_style: str
    recommended: bool


class OptimizeRequest(BaseModel):
    algorithm: str = Field(
        "nasa_milp",
        description="Алгоритм оптимизации: 'regulatory', 'nasa_milp', 'minimax_robust'",
    )
    scenario_type: str = Field("baseline", description="Тип сценария для симуляции")
    investments: InvestmentsInput = Field(default_factory=InvestmentsInput)
    horizon_years: Optional[List[int]] = Field(None, description="Список расчетных лет (по умолчанию 2035–2040)")
    discount_rate: float = Field(DEFAULT_DISCOUNT_RATE, ge=0.0, le=0.5)


class OptimizeResponse(BaseModel):
    algorithm: str
    metadata: OptimizerAlgorithmDTO
    channel_plans: Dict[int, Dict[str, ChannelPlanInput]]
    simulation: SimulationResponse
    comparison_with_regulatory: Dict[str, float]
