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

        # Rule 1: Critical Service Level >= 99%
        crit_sl = b_res.service_level_critical
        crit_viol = crit_sl < (MIN_CRITICAL_SERVICE_LEVEL - 1e-5)
        record_check(
            year=year,
            rule_code="CRITICAL_SERVICE_LEVEL",
            rule_name="Critical Demand Service Level",
            expected=f">={MIN_CRITICAL_SERVICE_LEVEL:.1%}",
            actual=f"{crit_sl:.2%}",
            message=(
                f"Critical service level is {crit_sl:.2%}, below mandatory {MIN_CRITICAL_SERVICE_LEVEL:.1%}. "
                f"Deficit: {b_res.deficit_critical:.2f} t."
            ) if crit_viol else "Critical service level satisfied.",
            violated=crit_viol,
        )

        # Rule 2: Total Service Level >= 97%
        tot_sl = b_res.service_level_total
        tot_viol = tot_sl < (MIN_TOTAL_SERVICE_LEVEL - 1e-5)
        record_check(
            year=year,
            rule_code="TOTAL_SERVICE_LEVEL",
            rule_name="Total Demand Service Level",
            expected=f">={MIN_TOTAL_SERVICE_LEVEL:.1%}",
            actual=f"{tot_sl:.2%}",
            message=(
                f"Total service level is {tot_sl:.2%}, below mandatory {MIN_TOTAL_SERVICE_LEVEL:.1%}. "
                f"Deficit: {b_res.deficit_total:.2f} t."
            ) if tot_viol else "Total service level satisfied.",
            violated=tot_viol,
        )

        # Rule 3: Tank Storage Capacity Overflow
        storage_viol = b_res.is_storage_overflow
        record_check(
            year=year,
            rule_code="STORAGE_CAPACITY_OVERFLOW",
            rule_name="Depot Tank Capacity",
            expected=f"<={b_res.storage_capacity_max:.1f} t",
            actual=f"{b_res.end_stock:.2f} t",
            message=(
                f"Tank overflow by {b_res.overflow_amount:.2f} t. "
                f"Closing stock {b_res.end_stock:.2f} t exceeds capacity {b_res.storage_capacity_max:.1f} t."
            ) if storage_viol else "Tank capacity respected.",
            violated=storage_viol,
        )

        # Rule 4: 45-day Reserve Compliance
        # Can be satisfied physically OR via contracted emergency reserve
        em_order = plan.orders.get(ChannelID.EMERGENCY)
        em_reserved = em_order.reserved_capacity if em_order else 0.0
        
        reserve_met = b_res.is_reserve_satisfied_physically or (
            (b_res.start_stock + em_reserved) >= (b_res.required_reserve_45d - 1e-5)
        )
        record_check(
            year=year,
            rule_code="RESERVE_45_DAYS",
            rule_name="45-Day Propellant Reserve",
            expected=f">={b_res.required_reserve_45d:.2f} t",
            actual=f"{b_res.start_stock:.2f} t (phys) + {em_reserved:.2f} t (emerg res)",
            message=(
                f"45-day reserve violated: physical stock ({b_res.start_stock:.2f} t) + Emergency reserve "
                f"({em_reserved:.2f} t) < required {b_res.required_reserve_45d:.2f} t."
            ) if not reserve_met else "45-day reserve requirement satisfied.",
            violated=not reserve_met,
        )

        # Rule 5: Channel Capacity Ceilings
        for ch_id, ch_cfg in channels.items():
            order = plan.orders.get(ch_id)
            if order:
                cap_viol = order.reserved_capacity > (ch_cfg.max_capacity + 1e-5)
                record_check(
                    year=year,
                    rule_code=f"CHANNEL_MAX_CAP_{ch_id.value.upper()}",
                    rule_name=f"{ch_id.value} Max Capacity",
                    expected=f"<={ch_cfg.max_capacity:.1f} t/yr",
                    actual=f"{order.reserved_capacity:.2f} t/yr",
                    message=(
                        f"Reserved capacity ({order.reserved_capacity:.2f} t) exceeds channel max "
                        f"({ch_cfg.max_capacity:.1f} t)."
                    ) if cap_viol else "Channel capacity within limits.",
                    violated=cap_viol,
                )

        # Rule 6: ISRU Availability & Operational gating
        if plan.isru_operational:
            isru_allowed = year >= 2038 and plan.isru_funded
            record_check(
                year=year,
                rule_code="LUNAR_ISRU_GATING",
                rule_name="Lunar-ISRU Commissioning Conditions",
                expected="Operational >= 2038 and fully funded before 2038",
                actual=f"Year={year}, Funded={plan.isru_funded}",
                message=(
                    f"Lunar-ISRU cannot operate in {year}: requires year >= 2038 and CAPEX funding prior to 2038."
                ) if not isru_allowed else "Lunar-ISRU gating satisfied.",
                violated=not isru_allowed,
            )

        # Rule 7: ZBO Earliest Year Gating (2036)
        if plan.zbo_invested and year < 2036:
            record_check(
                year=year,
                rule_code="ZBO_EARLIEST_YEAR",
                rule_name="ZBO Upgrade Earliest Year",
                expected="Operational >= 2036",
                actual=f"Year={year}",
                message="ZBO upgrade cannot be commissioned prior to 2036.",
                violated=True,
            )

    # 2. Multi-Year Consecutive Emergency Channel Check
    # "Emergency cannot be used as base channel for more than two consecutive years"
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
        year=violating_streak_end_year if violating_streak_end_year else "HORIZON",
        rule_code="EMERGENCY_CONSECUTIVE_LIMIT",
        rule_name="Emergency Consecutive Usage Ceiling",
        expected="<= 2 consecutive years as base channel",
        actual=f"{max_consecutive_emergency} consecutive years",
        message=(
            f"Emergency channel utilized as base supply for {max_consecutive_emergency} consecutive years "
            f"(threshold > {emergency_base_volume_threshold} t/yr), exceeding the maximum allowed of 2 years."
        ) if emergency_consecutive_viol else "Emergency channel usage duration compliant.",
        violated=emergency_consecutive_viol,
    )

    # 3. CAPEX Budget Limits
    # Limit 1: Through end of 2037 <= 1800 M c.u.
    capex_thru_2037 = sum(
        economics.yearly_economics[y].total_capex for y in config.horizon if y <= 2037
    )
    capex_2037_viol = capex_thru_2037 > (MAX_CAPEX_2037 + 1e-5)
    record_check(
        year=2037,
        rule_code="CAPEX_2037_LIMIT",
        rule_name="Cumulative CAPEX Through 2037",
        expected=f"<={MAX_CAPEX_2037:.1f} M c.u.",
        actual=f"{capex_thru_2037:.1f} M c.u.",
        message=(
            f"Cumulative CAPEX through 2037 is {capex_thru_2037:.1f} M c.u., exceeding budget limit "
            f"of {MAX_CAPEX_2037:.1f} M c.u. by {capex_thru_2037 - MAX_CAPEX_2037:.1f} M c.u."
        ) if capex_2037_viol else "CAPEX through 2037 within budget limit.",
        violated=capex_2037_viol,
    )

    # Limit 2: Cumulative CAPEX through 2040 <= 2800 M c.u.
    capex_thru_2040 = sum(
        economics.yearly_economics[y].total_capex for y in config.horizon if y <= 2040
    )
    capex_total_viol = capex_thru_2040 > (MAX_CAPEX_TOTAL + 1e-5)
    record_check(
        year=min(2040, config.end_year),
        rule_code="CAPEX_TOTAL_LIMIT",
        rule_name="Cumulative CAPEX Through 2040",
        expected=f"<={MAX_CAPEX_TOTAL:.1f} M c.u.",
        actual=f"{capex_thru_2040:.1f} M c.u.",
        message=(
            f"Cumulative CAPEX through 2040 is {capex_thru_2040:.1f} M c.u., exceeding total budget limit "
            f"of {MAX_CAPEX_TOTAL:.1f} M c.u. by {capex_thru_2040 - MAX_CAPEX_TOTAL:.1f} M c.u."
        ) if capex_total_viol else "Total CAPEX within budget limit.",
        violated=capex_total_viol,
    )

    is_feasible = len(violations) == 0

    return ConstraintCheckResult(
        violations=violations,
        all_checks=all_checks,
        is_feasible=is_feasible,
        total_violations_count=len(violations),
    )
