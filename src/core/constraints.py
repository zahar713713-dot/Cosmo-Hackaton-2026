"""
Constraint validation and boundary checks for the orbital fuel depot.
Strictly checks all hard constraints defined in the competition specifications:
- Critical service level >= 99%
- Total service level >= 97%
- CAPEX <= 1800 M c.u. through 2037
- Cumulative CAPEX <= 2800 M c.u. through 2040
- Tank capacity overflow (End_Stock <= Capacity_Max)
- Emergency channel consecutive years limit (<= 2 consecutive years as base supply)
- 45-day reserve compliance
- Channel capacity ceilings (Reserved <= Max_Capacity)
- Lunar-ISRU commissioning requirements (earliest 2038, prior funding required)
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from src.core.constants import (
    ChannelID,
    SupplyChannelConfig,
    DEFAULT_CHANNELS,
    MIN_CRITICAL_SERVICE_LEVEL,
    MIN_TOTAL_SERVICE_LEVEL,
    MAX_CAPEX_2037,
    MAX_CAPEX_TOTAL,
    YearlyPlan,
    SimulationConfig,
)
from src.core.balance import SimulationBalanceResult
from src.core.economics import SimulationEconomicsResult


class ConstraintViolation(BaseModel):
    """
    Structured record of a single constraint evaluation.
    """
    year: Union[int, str] = Field(..., description="Year of violation or 'HORIZON'")
    rule_code: str = Field(..., description="Machine-readable rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    expected: str = Field(..., description="Expected limit or condition")
    actual: str = Field(..., description="Actual calculated value")
    message: str = Field(..., description="Detailed diagnostic explanation")
    is_violated: bool = Field(..., description="True if constraint is breached")


class ConstraintCheckResult(BaseModel):
    """
    Collection of all constraint evaluations.
    """
    violations: List[ConstraintViolation] = Field(default_factory=list)
    all_checks: List[ConstraintViolation] = Field(default_factory=list)
    is_feasible: bool = Field(..., description="True if all hard constraints are fully satisfied")
    total_violations_count: int = Field(..., ge=0)


ConstraintSummary = ConstraintCheckResult


def validate_constraints(
    plans: Dict[int, YearlyPlan],
    balance: SimulationBalanceResult,
    economics: SimulationEconomicsResult,
    config: SimulationConfig,
    channels: Optional[Dict[ChannelID, SupplyChannelConfig]] = None,
    emergency_base_volume_threshold: float = 15.0,  # tons/yr threshold to classify as "base" supply
) -> ConstraintCheckResult:
    """
    Performs comprehensive numerical validation of all case rules.
    """
    if channels is None:
        channels = DEFAULT_CHANNELS

    all_checks: List[ConstraintViolation] = []
    violations: List[ConstraintViolation] = []

    def record_check(
        year: Union[int, str],
        rule_code: str,
        rule_name: str,
        expected: str,
        actual: str,
        message: str,
        violated: bool,
    ):
        v = ConstraintViolation(
            year=year,
            rule_code=rule_code,
            rule_name=rule_name,
            expected=expected,
            actual=actual,
            message=message,
            is_violated=violated,
        )
        all_checks.append(v)
        if violated:
            violations.append(v)

    # 1. Annual Service Levels and Inventory Checks
    for year in config.horizon:
        b_res = balance.yearly_results[year]
        plan = plans[year]

        # Правило 1: Критический SLA >= 99%
        crit_sl = b_res.service_level_critical
        crit_viol = crit_sl < (MIN_CRITICAL_SERVICE_LEVEL - 1e-5)
        record_check(
            year=year,
            rule_code="CRITICAL_SERVICE_LEVEL",
            rule_name="Критический уровень обслуживания (SLA)",
            expected=f">={MIN_CRITICAL_SERVICE_LEVEL:.1%}",
            actual=f"{crit_sl:.2%}",
            message=(
                f"Критический SLA равен {crit_sl:.2%}, что ниже нормы {MIN_CRITICAL_SERVICE_LEVEL:.1%}. "
                f"Дефицит пилотируемых миссий: {b_res.deficit_critical:.2f} т."
            ) if crit_viol else "Критический SLA удовлетворен.",
            violated=crit_viol,
        )

        # Правило 2: Общий SLA >= 97%
        tot_sl = b_res.service_level_total
        tot_viol = tot_sl < (MIN_TOTAL_SERVICE_LEVEL - 1e-5)
        record_check(
            year=year,
            rule_code="TOTAL_SERVICE_LEVEL",
            rule_name="Совокупный уровень обслуживания (SLA)",
            expected=f">={MIN_TOTAL_SERVICE_LEVEL:.1%}",
            actual=f"{tot_sl:.2%}",
            message=(
                f"Общий SLA составляет {tot_sl:.2%}, что ниже обязательной нормы {MIN_TOTAL_SERVICE_LEVEL:.1%}. "
                f"Дефицит: {b_res.deficit_total:.2f} т."
            ) if tot_viol else "Общий SLA удовлетворен.",
            violated=tot_viol,
        )

        # Правило 3: Вместимость баков ОТУ
        storage_viol = b_res.is_storage_overflow
        record_check(
            year=year,
            rule_code="STORAGE_CAPACITY_OVERFLOW",
            rule_name="Вместимость баков ОТУ",
            expected=f"<={b_res.storage_capacity_max:.1f} т",
            actual=f"{b_res.end_stock:.2f} т",
            message=(
                f"Переполнение баков на {b_res.overflow_amount:.2f} т. "
                f"Конечный остаток {b_res.end_stock:.2f} т превышает предельную вместимость {b_res.storage_capacity_max:.1f} т."
            ) if storage_viol else "Вместимость баков соблюдена.",
            violated=storage_viol,
        )

        # Правило 4: Неснижаемый 45-дневный буфер топлива
        # Может обеспечиваться физически или законтрактованной бронью Emergency
        em_order = plan.orders.get(ChannelID.EMERGENCY)
        em_reserved = em_order.reserved_capacity if em_order else 0.0
        
        reserve_met = b_res.is_reserve_satisfied_physically or (
            (b_res.start_stock + em_reserved) >= (b_res.required_reserve_45d - 1e-5)
        )
        record_check(
            year=year,
            rule_code="RESERVE_45_DAYS",
            rule_name="45-дневный страховой буфер топлива",
            expected=f">={b_res.required_reserve_45d:.2f} т",
            actual=f"{b_res.start_stock:.2f} т (физ.) + {em_reserved:.2f} т (бронь Emergency)",
            message=(
                f"Нарушен 45-дневный буфер: физический запас ({b_res.start_stock:.2f} т) + аварийная бронь "
                f"({em_reserved:.2f} т) < требуемых {b_res.required_reserve_45d:.2f} т."
            ) if not reserve_met else "Норма 45-дневного страхового резерва соблюдена.",
            violated=not reserve_met,
        )

        # Правило 5: Предельная пропускная способность каналов
        for ch_id, ch_cfg in channels.items():
            order = plan.orders.get(ch_id)
            if order:
                cap_viol = order.reserved_capacity > (ch_cfg.max_capacity + 1e-5)
                record_check(
                    year=year,
                    rule_code=f"CHANNEL_MAX_CAP_{ch_id.value.upper()}",
                    rule_name=f"Предельная мощность канала {ch_cfg.name}",
                    expected=f"<={ch_cfg.max_capacity:.1f} т/год",
                    actual=f"{order.reserved_capacity:.2f} т/год",
                    message=(
                        f"Забронированная мощность ({order.reserved_capacity:.2f} т) превышает "
                        f"предел канала ({ch_cfg.max_capacity:.1f} т/год)."
                    ) if cap_viol else "Бронирование в пределах мощности канала.",
                    violated=cap_viol,
                )

        # Правило 6: Условия ввода Lunar-ISRU
        if plan.isru_operational:
            isru_allowed = year >= 2038 and plan.isru_funded
            record_check(
                year=year,
                rule_code="LUNAR_ISRU_GATING",
                rule_name="Условия ввода Lunar-ISRU",
                expected="Ввод >= 2038 г. при условии полного финансирования до 2038 г.",
                actual=f"Год={year}, Профинансировано={plan.isru_funded}",
                message=(
                    f"Lunar-ISRU не может поставлять топливо в {year} г.: требуется год >= 2038 и полное финансирование CAPEX до 2038 г."
                ) if not isru_allowed else "Условия готовности Lunar-ISRU соблюдены.",
                violated=not isru_allowed,
            )

        # Правило 7: Минимальный срок ввода ZBO (2036)
        if plan.zbo_invested and year < 2036:
            record_check(
                year=year,
                rule_code="ZBO_EARLIEST_YEAR",
                rule_name="Минимальный срок ввода ZBO",
                expected="Ввод >= 2036 г.",
                actual=f"Год={year}",
                message="Модернизация ZBO не может быть введена ранее 2036 года.",
                violated=True,
            )

    # 2. Ограничение непрерывного использования канала Emergency
    consecutive_emergency_years = 0
    max_consecutive_emergency = 0
    violating_streak_end_year: Optional[int] = None

    for year in config.horizon:
        plan = plans[year]
        em_order = plan.orders.get(ChannelID.EMERGENCY)
        em_volume = em_order.order_volume if em_order else 0.0

        if em_volume >= emergency_base_volume_threshold:
            consecutive_emergency_years += 1
            if consecutive_emergency_years > max_consecutive_emergency:
                max_consecutive_emergency = consecutive_emergency_years
            if consecutive_emergency_years > 2 and violating_streak_end_year is None:
                violating_streak_end_year = year
        else:
            consecutive_emergency_years = 0

    emergency_consecutive_viol = max_consecutive_emergency > 2
    record_check(
        year=violating_streak_end_year if violating_streak_end_year else "ГОРИЗОНТ",
        rule_code="EMERGENCY_CONSECUTIVE_LIMIT",
        rule_name="Лимит непрерывного использования канала Emergency",
        expected="<= 2 лет подряд как базовый канал",
        actual=f"{max_consecutive_emergency} года(лет) подряд",
        message=(
            f"Канал Emergency использовался как базовый {max_consecutive_emergency} года подряд "
            f"(отбор > {emergency_base_volume_threshold} т/год), что превышает лимит 2 года подряд."
        ) if emergency_consecutive_viol else "Срок использования канала Emergency в норме.",
        violated=emergency_consecutive_viol,
    )

    # 3. Лимиты бюджета CAPEX
    # Лимит 1: До конца 2037 г. <= 1800 млн у.е.
    capex_thru_2037 = sum(
        economics.yearly_economics[y].total_capex for y in config.horizon if y <= 2037
    )
    capex_2037_viol = capex_thru_2037 > (MAX_CAPEX_2037 + 1e-5)
    record_check(
        year=2037,
        rule_code="CAPEX_2037_LIMIT",
        rule_name="Суммарный CAPEX до конца 2037 года",
        expected=f"<={MAX_CAPEX_2037:.1f} млн у.е.",
        actual=f"{capex_thru_2037:.1f} млн у.е.",
        message=(
            f"Суммарный CAPEX до 2037 г. составляет {capex_thru_2037:.1f} млн у.е., превышая лимит "
            f"в {MAX_CAPEX_2037:.1f} млн у.е. на {capex_thru_2037 - MAX_CAPEX_2037:.1f} млн у.е."
        ) if capex_2037_viol else "CAPEX до 2037 г. в пределах директивного лимита.",
        violated=capex_2037_viol,
    )

    # Лимит 2: Совокупный CAPEX программы <= 2800 млн у.е.
    capex_thru_2040 = sum(
        economics.yearly_economics[y].total_capex for y in config.horizon if y <= 2040
    )
    capex_total_viol = capex_thru_2040 > (MAX_CAPEX_TOTAL + 1e-5)
    record_check(
        year=min(2040, config.end_year),
        rule_code="CAPEX_TOTAL_LIMIT",
        rule_name="Совокупный CAPEX программы до 2040 года",
        expected=f"<={MAX_CAPEX_TOTAL:.1f} млн у.е.",
        actual=f"{capex_thru_2040:.1f} млн у.е.",
        message=(
            f"Совокупный CAPEX программы равен {capex_thru_2040:.1f} млн у.е., превышая утвержденный лимит "
            f"в {MAX_CAPEX_TOTAL:.1f} млн у.е. на {capex_thru_2040 - MAX_CAPEX_TOTAL:.1f} млн у.е."
        ) if capex_total_viol else "Совокупный CAPEX программы в пределах бюджета.",
        violated=capex_total_viol,
    )

    is_feasible = len(violations) == 0

    return ConstraintCheckResult(
        violations=violations,
        all_checks=all_checks,
        is_feasible=is_feasible,
        total_violations_count=len(violations),
    )
