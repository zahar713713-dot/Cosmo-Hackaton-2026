"""
FastAPI route handlers connecting the calculation engine with the presentation layer.
Implements criteria 19 & 20 (operator controls, scenario comparison, sensitivity, and exports).
"""

import io
import os
import zipfile
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse, Response, StreamingResponse

from src.core.constants import (
    ChannelID,
    DemandRecord,
    SupplyChannelConfig,
    StorageConfig,
    DEFAULT_CHANNELS,
    BASE_STORAGE,
    ZBO_STORAGE,
    BASE_DEMAND,
    DEFAULT_DISCOUNT_RATE,
    ChannelOrder,
    YearlyPlan,
    SimulationConfig,
)
from src.core.balance import calculate_material_balance
from src.core.economics import calculate_economics
from src.core.constraints import validate_constraints
from src.core.scenarios import (
    ScenarioType,
    GeopoliticalShockConfig,
    get_scenario_modifier,
    apply_scenario,
    SimulationRunOutput,
)
from src.core.exporter import (
    export_to_excel,
    export_to_csv,
    generate_summary_kpi_dataframe,
    generate_material_balance_dataframe,
    generate_economics_dataframe,
    generate_constraints_log_dataframe,
)
from src.core.optimizers import (
    OptimizerAlgorithm,
    ALGORITHM_REGISTRY,
    optimize_plans,
)
from src.api.schemas import (
    SimulationRequest,
    SimulationResponse,
    YearlyBalanceDTO,
    YearlyEconomicsDTO,
    ViolationDTO,
    CompareRequest,
    CompareResponse,
    SensitivityRequest,
    SensitivityPoint,
    SensitivityResponse,
    GeopoliticalShockRequest,
    GeopoliticalShockResponse,
    OptimizerAlgorithmDTO,
    OptimizeRequest,
    OptimizeResponse,
    ChannelPlanInput,
)

router = APIRouter(prefix="/api/v1", tags=["Orbital Fuel Depot Planning API"])


def _build_core_objects_from_request(
    req: SimulationRequest,
) -> tuple[Dict[int, YearlyPlan], SimulationConfig, ScenarioType]:
    """
    Translates API request DTOs into strongly typed core domain objects.
    """
    years = sorted(req.channel_plans.keys())
    if not years:
        raise HTTPException(status_code=422, detail="Планы каналов снабжения не могут быть пустыми.")

    config = SimulationConfig(
        start_year=min(years),
        end_year=max(years),
        discount_rate=req.discount_rate,
        initial_stock_2035=req.initial_stock_2035,
    )

    # Map string to ScenarioType enum
    type_map = {
        "baseline": ScenarioType.BASELINE,
        "stress": ScenarioType.MANDATORY_STRESS,
        "high_demand": ScenarioType.HIGH_DEMAND,
        "low_demand": ScenarioType.LOW_DEMAND,
        "custom": ScenarioType.BASELINE,
        "geopolitical": ScenarioType.GEOPOLITICAL_SHOCK,
    }
    scen_type = type_map.get(req.scenario_type, ScenarioType.BASELINE)

    inv = req.investments
    plans: Dict[int, YearlyPlan] = {}

    for y in config.horizon:
        year_orders_input = req.channel_plans.get(y, {})
        core_orders: Dict[ChannelID, ChannelOrder] = {}

        for ch in ChannelID:
            if ch in year_orders_input:
                inp = year_orders_input[ch]
                core_orders[ch] = ChannelOrder(
                    channel_id=ch,
                    reserved_capacity=inp.reserved_capacity,
                    order_volume=inp.target_order_volume,
                )
            else:
                core_orders[ch] = ChannelOrder(
                    channel_id=ch,
                    reserved_capacity=0.0,
                    order_volume=0.0,
                )

        plans[y] = YearlyPlan(
            year=y,
            orders=core_orders,
            zbo_invested=(inv.zbo_year is not None and y >= inv.zbo_year),
            isru_funded=(inv.isru_enabled and y >= 2037),
            isru_operational=(inv.isru_enabled and y >= 2038),
            earth_new_option_purchased=(
                inv.earth_new_enabled and inv.earth_new_option_year is not None and y >= inv.earth_new_option_year
            ),
            earth_new_exercised=(
                inv.earth_new_enabled and inv.earth_new_exercise_year is not None and y >= inv.earth_new_exercise_year
            ),
            earth_new_operational=(
                inv.earth_new_enabled and inv.earth_new_exercise_year is not None and y >= (inv.earth_new_exercise_year + 2)
            ),
        )

    return plans, config, scen_type


def _format_simulation_response(run: SimulationRunOutput) -> SimulationResponse:
    """
    Transforms core domain results into detailed JSON API response.
    """
    b = run.balance
    e = run.economics
    c = run.constraints

    balance_dtos: List[YearlyBalanceDTO] = []
    for y, y_bal in sorted(b.yearly_results.items()):
        em_res = 0.0
        for chk in c.all_checks:
            if chk.rule_code == "RESERVE_45_DAYS" and chk.year == y:
                import re
                m = re.search(r"\+\s*([\d.]+)\s*т\s*\(бронь", chk.actual)
                if m:
                    em_res = float(m.group(1))
                break
        balance_dtos.append(
            YearlyBalanceDTO(
                year=y,
                start_stock=y_bal.start_stock,
                gross_delivery=y_bal.gross_delivery,
                losses=y_bal.losses,
                net_available_inflow=y_bal.net_available_inflow,
                total_fuel_available=y_bal.total_fuel_available,
                demand_total=y_bal.demand_total,
                demand_critical=y_bal.demand_critical,
                served_demand_total=y_bal.served_demand_total,
                served_demand_critical=y_bal.served_demand_critical,
                deficit_total=y_bal.deficit_total,
                deficit_critical=y_bal.deficit_critical,
                end_stock=y_bal.end_stock,
                storage_capacity_max=y_bal.storage_capacity_max,
                is_storage_overflow=y_bal.is_storage_overflow,
                overflow_amount=y_bal.overflow_amount,
                required_reserve_45d=y_bal.required_reserve_45d,
                is_reserve_satisfied=y_bal.is_reserve_satisfied_physically,
                service_level_total=y_bal.service_level_total,
                service_level_critical=y_bal.service_level_critical,
                channel_deliveries={k.value: v for k, v in y_bal.channel_deliveries.items()},
                emergency_reserve=round(em_res, 4),
                guaranteed_buffer_total=round(y_bal.end_stock + em_res, 4),
            )
        )

    econ_dtos: List[YearlyEconomicsDTO] = []
    for y, y_econ in sorted(e.yearly_economics.items()):
        econ_dtos.append(
            YearlyEconomicsDTO(
                year=y,
                procurement_cost=y_econ.procurement_cost,
                reservation_cost=y_econ.reservation_cost,
                storage_holding_cost=y_econ.storage_holding_cost,
                zbo_fixed_opex=y_econ.zbo_fixed_opex,
                isru_fixed_opex=y_econ.isru_fixed_opex,
                initial_stock_acquisition_cost=y_econ.initial_stock_acquisition_cost,
                total_opex=y_econ.total_opex,
                capex_zbo=y_econ.capex_zbo,
                capex_earth_new=y_econ.capex_earth_new,
                capex_isru=y_econ.capex_isru,
                total_capex=y_econ.total_capex,
                total_expenditure=y_econ.total_expenditure,
                discount_factor=y_econ.discount_factor,
                discounted_expenditure=y_econ.discounted_expenditure,
                channel_payments={k.value: v.total_channel_payment for k, v in y_econ.channel_costs.items()},
            )
        )

    violation_dtos: List[ViolationDTO] = []
    for v in c.all_checks:
        violation_dtos.append(
            ViolationDTO(
                year=str(v.year),
                rule_code=v.rule_code,
                rule_name=v.rule_name,
                expected=v.expected,
                actual=v.actual,
                message=v.message,
                is_violated=v.is_violated,
            )
        )

    summary_kpi = {
        "is_feasible": c.is_feasible,
        "total_demand_tons": round(sum(r.demand_total for r in b.yearly_results.values()), 2),
        "total_served_demand_tons": round(b.total_served_demand, 2),
        "total_deficit_tons": round(b.total_deficit, 2),
        "average_service_level_total": round(b.average_service_level_total, 4),
        "average_service_level_critical": round(b.average_service_level_critical, 4),
        "total_gross_delivery_tons": round(b.total_gross_delivery, 2),
        "total_losses_tons": round(b.total_losses, 2),
        "total_opex_m_cu": round(e.total_opex, 2),
        "total_capex_m_cu": round(e.total_capex, 2),
        "total_cost_m_cu": round(e.total_undiscounted_cost, 2),
        "npv_cost_m_cu": round(e.total_npv_cost, 2),
        "cost_per_ton_served_m_cu": round(e.cost_per_ton_served, 4),
        "discounted_cost_per_ton_served_m_cu": round(e.discounted_cost_per_ton_served, 4),
    }

    return SimulationResponse(
        scenario_type=run.scenario_type.value,
        scenario_name=run.scenario_name,
        is_feasible=c.is_feasible,
        summary_kpi=summary_kpi,
        yearly_balance=balance_dtos,
        yearly_economics=econ_dtos,
        violations=violation_dtos,
    )


@router.get("/scenarios/defaults", summary="Справочные параметры кейса")
def get_defaults():
    """
    Возвращает стандартные справочные параметры кейса:
    каналы снабжения, спрос (базовый, высокий, низкий), параметры хранилища и правила стресс-теста.
    """
    channels_dict = {}
    for ch_id, ch in DEFAULT_CHANNELS.items():
        channels_dict[ch_id.value] = {
            "name": ch.name,
            "max_capacity": ch.max_capacity,
            "var_cost": ch.var_cost,
            "res_tariff": ch.res_tariff,
            "take_or_pay": ch.take_or_pay,
            "lead_time_months": ch.lead_time_months,
            "lead_time_weeks": ch.lead_time_weeks,
            "reliability": ch.annual_reliability,
        }

    demand_dict = {}
    for y, d in BASE_DEMAND.items():
        demand_dict[y] = {
            "base_total": d.base_total,
            "base_critical": d.base_critical,
            "low_total": d.low_total,
            "high_total": d.high_total,
        }

    return {
        "channels": channels_dict,
        "demand": demand_dict,
        "storage": {
            "base": {
                "capacity_max": BASE_STORAGE.capacity_max,
                "throughput_loss_rate": BASE_STORAGE.throughput_loss_rate,
                "holding_cost_rate": BASE_STORAGE.holding_cost_rate,
                "capex": BASE_STORAGE.capex_required,
                "add_opex": BASE_STORAGE.additional_opex_annual,
            },
            "zbo_modernized": {
                "capacity_max": ZBO_STORAGE.capacity_max,
                "throughput_loss_rate": ZBO_STORAGE.throughput_loss_rate,
                "holding_cost_rate": ZBO_STORAGE.holding_cost_rate,
                "capex": ZBO_STORAGE.capex_required,
                "add_opex": ZBO_STORAGE.additional_opex_annual,
                "min_year": ZBO_STORAGE.min_available_year,
            },
        },
        "mandatory_stress_rules": {
            "demand_multiplier_2038_2040": 1.15,
            "earth_price_multiplier_2038_2039": 1.25,
            "isru_actual_delivery_fractions": {2038: 0.55, 2039: 0.75, 2040: 1.00},
            "loss_ceiling_2038_2040": 0.02,
        },
        "limits": {
            "min_total_service_level": 0.97,
            "min_critical_service_level": 0.99,
            "max_capex_2037": 1800.0,
            "max_capex_total": 2800.0,
            "reserve_days": 45,
            "default_discount_rate": 0.08,
        },
    }


@router.post("/simulate", response_model=SimulationResponse, summary="Запуск расчета симуляции")
def simulate(request: SimulationRequest):
    """
    Выполняет расчёт материального баланса, финансовых затрат и проверку ограничений.
    """
    plans, config, scen_type = _build_core_objects_from_request(request)

    # Optional custom overrides
    if request.custom_params and request.custom_params.loss_rate_override is not None:
        # custom loss rate
        pass

    run_output = apply_scenario(plans=plans, scenario_type=scen_type, config=config)
    return _format_simulation_response(run_output)


@router.post("/simulate/compare", response_model=CompareResponse, summary="Сравнение нескольких сценариев")
def compare_scenarios(request: CompareRequest):
    """
    Принимает от 2 до 5 планов (например, Baseline vs Mandatory Stress vs Geopolitical Shock)
    и возвращает сопоставительную матрицу и дельты ключевых показателей.
    """
    runs: List[tuple[str, SimulationRunOutput]] = []

    for idx, scen_req in enumerate(request.scenarios):
        label = (
            request.labels[idx]
            if (request.labels and idx < len(request.labels))
            else f"Сценарий {idx + 1} ({scen_req.scenario_type})"
        )
        plans, config, scen_type = _build_core_objects_from_request(scen_req)
        output = apply_scenario(plans=plans, scenario_type=scen_type, config=config)
        runs.append((label, output))

    summary_matrix = []
    base_kpi = None

    for label, run in runs:
        b = run.balance
        e = run.economics
        c = run.constraints

        kpi_row = {
            "label": label,
            "scenario_type": run.scenario_type.value,
            "is_feasible": c.is_feasible,
            "violations_count": c.total_violations_count,
            "served_demand_tons": round(b.total_served_demand, 2),
            "total_deficit_tons": round(b.total_deficit, 2),
            "service_level_total_pct": round(b.average_service_level_total * 100, 2),
            "service_level_critical_pct": round(b.average_service_level_critical * 100, 2),
            "total_losses_tons": round(b.total_losses, 2),
            "total_opex_m_cu": round(e.total_opex, 2),
            "total_capex_m_cu": round(e.total_capex, 2),
            "total_cost_m_cu": round(e.total_undiscounted_cost, 2),
            "npv_cost_m_cu": round(e.total_npv_cost, 2),
            "cost_per_ton_served_m_cu": round(e.cost_per_ton_served, 4),
        }
        summary_matrix.append(kpi_row)
        if base_kpi is None:
            base_kpi = kpi_row

    deltas_vs_first = []
    for row in summary_matrix[1:]:
        delta_row = {
            "label": row["label"],
            "delta_cost_m_cu": round(row["total_cost_m_cu"] - base_kpi["total_cost_m_cu"], 2),
            "delta_npv_m_cu": round(row["npv_cost_m_cu"] - base_kpi["npv_cost_m_cu"], 2),
            "delta_deficit_tons": round(row["total_deficit_tons"] - base_kpi["total_deficit_tons"], 2),
            "delta_service_level_pct": round(
                row["service_level_total_pct"] - base_kpi["service_level_total_pct"], 2
            ),
        }
        deltas_vs_first.append(delta_row)

    return CompareResponse(summary_matrix=summary_matrix, deltas_vs_first=deltas_vs_first)


@router.post("/export/{format}", summary="Экспорт отчета в Excel (XLSX) или CSV")
def export_results(
    request: SimulationRequest,
    format: str = Path(..., description="Формат выгрузки: 'xlsx' или 'csv'"),
):
    """
    Генерирует машиночитаемый отчет со всеми листами (Summary_KPI, Material_Balance, Economics, Constraints).
    """
    plans, config, scen_type = _build_core_objects_from_request(request)
    base_run = apply_scenario(plans=plans, scenario_type=ScenarioType.BASELINE, config=config)
    stress_run = apply_scenario(plans=plans, scenario_type=ScenarioType.MANDATORY_STRESS, config=config)

    format_clean = format.lower().strip()

    if format_clean == "xlsx":
        output_buffer = io.BytesIO()
        df_kpi = generate_summary_kpi_dataframe(base_run, stress_run)
        df_bal = generate_material_balance_dataframe(base_run)
        df_econ = generate_economics_dataframe(base_run)
        df_con = generate_constraints_log_dataframe(base_run)

        df_bal_stress = generate_material_balance_dataframe(stress_run)
        df_econ_stress = generate_economics_dataframe(stress_run)
        df_con_stress = generate_constraints_log_dataframe(stress_run)

        import pandas as pd
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            df_kpi.to_excel(writer, sheet_name="Summary_KPI", index=False)
            df_bal.to_excel(writer, sheet_name="Material_Balance_Base", index=False)
            df_econ.to_excel(writer, sheet_name="Economics_Base", index=False)
            df_con.to_excel(writer, sheet_name="Constraints_Base", index=False)
            df_bal_stress.to_excel(writer, sheet_name="Material_Balance_Stress", index=False)
            df_econ_stress.to_excel(writer, sheet_name="Economics_Stress", index=False)
            df_con_stress.to_excel(writer, sheet_name="Constraints_Stress", index=False)

        output_buffer.seek(0)
        return StreamingResponse(
            output_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=fuel_depot_planning_report.xlsx"},
        )

    elif format_clean == "csv":
        zip_buffer = io.BytesIO()
        df_bal = generate_material_balance_dataframe(base_run)
        df_econ = generate_economics_dataframe(base_run)
        df_con = generate_constraints_log_dataframe(base_run)

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("material_balance.csv", df_bal.to_csv(index=False, encoding="utf-8-sig"))
            zip_file.writestr("economics.csv", df_econ.to_csv(index=False, encoding="utf-8-sig"))
            zip_file.writestr("constraints_log.csv", df_con.to_csv(index=False, encoding="utf-8-sig"))

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=fuel_depot_csv_bundle.zip"},
        )

    raise HTTPException(status_code=400, detail="Поддерживаются только форматы 'xlsx' и 'csv'.")


@router.post("/stress/sensitivity", response_model=SensitivityResponse, summary="Анализ чувствительности (Tornado)")
def analyze_sensitivity(request: SensitivityRequest):
    """
    Запускает сценарный анализ чувствительности (Tornado diagram):
    варьирование цен на земные пуски (-20%..+40%), сдвиг готовности ISRU (на 1-2 года), колебания спроса.
    """
    plans, config, _ = _build_core_objects_from_request(request.base_request)
    base_run = apply_scenario(plans=plans, scenario_type=ScenarioType.BASELINE, config=config)
    base_cost = base_run.economics.total_undiscounted_cost
    base_npv = base_run.economics.total_npv_cost

    points: List[SensitivityPoint] = []
    thresholds: List[str] = []

    # 1. Price variation on Earth-Core and Flex
    for delta_p in request.price_shock_range:
        mult = 1.0 + delta_p
        price_mult = {y: {ChannelID.EARTH_CORE: mult, ChannelID.EARTH_FLEX: mult} for y in config.horizon}
        econ_res = calculate_economics(
            plans=plans,
            balance_results=base_run.balance,
            config=config,
            price_multipliers=price_mult,
        )
        con_res = validate_constraints(plans, base_run.balance, econ_res, config)

        points.append(
            SensitivityPoint(
                parameter="Цена запусков с Земли (Core/Flex)",
                variation=f"{delta_p:+.0%}",
                total_cost=round(econ_res.total_undiscounted_cost, 2),
                npv_cost=round(econ_res.total_npv_cost, 2),
                total_deficit=round(base_run.balance.total_deficit, 2),
                min_service_level=round(base_run.balance.average_service_level_total, 4),
                is_feasible=con_res.is_feasible,
            )
        )

    # 2. Demand variation
    for delta_d in request.demand_shock_range:
        mult = 1.0 + delta_d
        shocked_demand = {}
        for y in config.horizon:
            raw = BASE_DEMAND[y]
            shocked_demand[y] = DemandRecord(
                year=y,
                base_total=round(raw.base_total * mult, 2),
                base_critical=round(raw.base_critical * mult, 2),
            )
        bal_res = calculate_material_balance(plans=plans, demand=shocked_demand, config=config)
        econ_res = calculate_economics(plans=plans, balance_results=bal_res, config=config)
        con_res = validate_constraints(plans=plans, balance=bal_res, economics=econ_res, config=config)

        pt = SensitivityPoint(
            parameter="Уровень общего спроса",
            variation=f"{delta_d:+.0%}",
            total_cost=round(econ_res.total_undiscounted_cost, 2),
            npv_cost=round(econ_res.total_npv_cost, 2),
            total_deficit=round(bal_res.total_deficit, 2),
            min_service_level=round(bal_res.average_service_level_total, 4),
            is_feasible=con_res.is_feasible,
        )
        points.append(pt)
        if not con_res.is_feasible and delta_d > 0:
            thresholds.append(f"Рост спроса свыше {delta_d:+.0%} приводит к дефициту КРТ и нарушению SLA.")

    # 3. ISRU Delay (1 or 2 years)
    for delay in request.isru_delay_years:
        if delay == 0:
            continue
        delayed_plans = {}
        for y, p in plans.items():
            dp = p.model_copy(deep=True)
            # if delayed, ISRU is operational only from (2038 + delay)
            if y < (2038 + delay):
                dp.isru_operational = False
                if ChannelID.LUNAR_ISRU in dp.orders:
                    dp.orders[ChannelID.LUNAR_ISRU].reserved_capacity = 0.0
                    dp.orders[ChannelID.LUNAR_ISRU].order_volume = 0.0
            delayed_plans[y] = dp

        bal_res = calculate_material_balance(plans=delayed_plans, demand=BASE_DEMAND, config=config)
        econ_res = calculate_economics(plans=delayed_plans, balance_results=bal_res, config=config)
        con_res = validate_constraints(plans=delayed_plans, balance=bal_res, economics=econ_res, config=config)

        points.append(
            SensitivityPoint(
                parameter="Задержка ввода Lunar-ISRU",
                variation=f"+{delay} год(а)",
                total_cost=round(econ_res.total_undiscounted_cost, 2),
                npv_cost=round(econ_res.total_npv_cost, 2),
                total_deficit=round(bal_res.total_deficit, 2),
                min_service_level=round(bal_res.average_service_level_total, 4),
                is_feasible=con_res.is_feasible,
            )
        )
        if not con_res.is_feasible:
            thresholds.append(
                f"Сдвиг ввода ISRU на {delay} г. вызывает дефицит {bal_res.total_deficit:.1f} т без компенсации Землей."
            )

    # Calculate elasticity
    # Elasticity = % change in Total Cost / % change in parameter
    price_point_plus_20 = next((p for p in points if p.parameter.startswith("Цена") and p.variation == "+20%"), None)
    price_elasticity = 0.0
    if price_point_plus_20:
        cost_pct = (price_point_plus_20.total_cost - base_cost) / base_cost
        price_elasticity = cost_pct / 0.20

    demand_point_plus_20 = next((p for p in points if p.parameter.startswith("Уровень") and p.variation == "+20%"), None)
    demand_elasticity = 0.0
    if demand_point_plus_20:
        cost_pct = (demand_point_plus_20.total_cost - base_cost) / base_cost
        demand_elasticity = cost_pct / 0.20

    return SensitivityResponse(
        tornado_points=points,
        cost_elasticities={
            "launch_price_elasticity": round(price_elasticity, 4),
            "demand_elasticity": round(demand_elasticity, 4),
        },
        critical_thresholds=thresholds,
    )


@router.post("/geopolitical-shock", response_model=GeopoliticalShockResponse, summary="Бонусный геополитический шок (+5 баллов)")
def apply_geopolitical_shock(request: GeopoliticalShockRequest):
    """
    Моделирует тарифные и санкционные шоки на земные поставки.
    """
    plans, config, _ = _build_core_objects_from_request(request.base_request)
    base_run = apply_scenario(plans=plans, scenario_type=ScenarioType.BASELINE, config=config)

    geo_config = GeopoliticalShockConfig(
        start_year=request.start_year,
        end_year=request.end_year,
        earth_core_price_multiplier=request.earth_core_price_multiplier,
        earth_flex_price_multiplier=request.earth_flex_price_multiplier,
        earth_core_capacity_cap=request.earth_core_capacity_cap,
        description=request.description,
    )

    geo_run = apply_scenario(
        plans=plans,
        scenario_type=ScenarioType.GEOPOLITICAL_SHOCK,
        config=config,
        geo_config=geo_config,
    )

    cost_delta = round(geo_run.economics.total_undiscounted_cost - base_run.economics.total_undiscounted_cost, 2)
    npv_delta = round(geo_run.economics.total_npv_cost - base_run.economics.total_npv_cost, 2)
    service_delta = round(
        (geo_run.balance.average_service_level_total - base_run.balance.average_service_level_total) * 100, 2
    )

    narrative = (
        f"В период {request.start_year}–{request.end_year} гг. реализован геополитический сценарий: "
        f"рост тарифов Earth-Core ({request.earth_core_price_multiplier:+.0%}) и Earth-Flex "
        f"({request.earth_flex_price_multiplier:+.0%}). "
        f"Прирост совокупных затрат составил {cost_delta:+.2f} млн у.е. (LCC / NPV delta: {npv_delta:+.2f} млн у.е.). "
        f"Статус исполнимости плана: {'PASS' if geo_run.constraints.is_feasible else 'FAIL'}."
    )

    return GeopoliticalShockResponse(
        simulation_result=_format_simulation_response(geo_run),
        cost_delta_vs_baseline=cost_delta,
        npv_delta_vs_baseline=npv_delta,
        service_delta_vs_baseline=service_delta,
        narrative_impact=narrative,
    )


@router.get(
    "/optimize/algorithms",
    response_model=List[OptimizerAlgorithmDTO],
    summary="Справочник доступных математических ядер оптимизации",
)
def get_optimization_algorithms():
    """
    Возвращает список доступных алгоритмических ядер (Регламент ТЗ, NASA MILP, Робастный Minimax)
    с их научным обоснованием, описанием и целевыми метриками.
    """
    res = []
    for algo_enum, meta in ALGORITHM_REGISTRY.items():
        res.append(
            OptimizerAlgorithmDTO(
                id=meta.id,
                name=meta.name,
                short_name=meta.short_name,
                foundation=meta.foundation,
                description=meta.description,
                target_metric=meta.target_metric,
                badge_style=meta.badge_style,
                recommended=meta.recommended,
            )
        )
    return res


@router.post(
    "/optimize",
    response_model=OptimizeResponse,
    summary="Автоматическая оптимизация плана снабжения выбранным ядром",
)
def run_optimization(request: OptimizeRequest):
    """
    Выполняет расчет оптимальных объемов бронирования и отбора по 5 каналам
    с использованием выбранного алгоритма (Регламент ТЗ / NASA MILP / Робастный Minimax).
    Возвращает готовый план и результаты физико-экономической симуляции.
    """
    try:
        algo_enum = OptimizerAlgorithm(request.algorithm)
    except ValueError:
        algo_enum = OptimizerAlgorithm.NASA_MILP

    inv_dict = request.investments.model_dump()
    years = request.horizon_years or list(range(2035, 2041))
    config = SimulationConfig(
        start_year=min(years),
        end_year=max(years),
        discount_rate=request.discount_rate,
    )

    type_map = {
        "baseline": ScenarioType.BASELINE,
        "stress": ScenarioType.MANDATORY_STRESS,
        "high_demand": ScenarioType.HIGH_DEMAND,
        "low_demand": ScenarioType.LOW_DEMAND,
        "geopolitical": ScenarioType.GEOPOLITICAL_SHOCK,
    }
    scen_type = type_map.get(request.scenario_type, ScenarioType.BASELINE)

    # 1. Compute optimized plans with selected algorithm
    opt_plans = optimize_plans(
        algorithm=algo_enum,
        investments_state=inv_dict,
        years=years,
        discount_rate=request.discount_rate,
    )
    opt_run = apply_scenario(plans=opt_plans, scenario_type=scen_type, config=config)

    # 2. Compute benchmark regulatory plans for delta calculation
    reg_plans = optimize_plans(
        algorithm=OptimizerAlgorithm.REGULATORY,
        investments_state=inv_dict,
        years=years,
        discount_rate=request.discount_rate,
    )
    reg_run = apply_scenario(plans=reg_plans, scenario_type=scen_type, config=config)

    reg_npv = reg_run.economics.total_npv_cost
    cur_npv = opt_run.economics.total_npv_cost
    delta_npv = round(reg_npv - cur_npv, 2)
    savings_pct = round((delta_npv / reg_npv * 100.0), 2) if reg_npv > 0 else 0.0

    # Format plans for response
    channel_plans_out: Dict[int, Dict[str, ChannelPlanInput]] = {}
    for y in sorted(opt_plans.keys()):
        channel_plans_out[y] = {}
        for ch_id, ch_order in opt_plans[y].orders.items():
            channel_plans_out[y][ch_id.value] = ChannelPlanInput(
                reserved_capacity=ch_order.reserved_capacity,
                target_order_volume=ch_order.order_volume,
            )

    meta = ALGORITHM_REGISTRY[algo_enum]
    meta_dto = OptimizerAlgorithmDTO(
        id=meta.id,
        name=meta.name,
        short_name=meta.short_name,
        foundation=meta.foundation,
        description=meta.description,
        target_metric=meta.target_metric,
        badge_style=meta.badge_style,
        recommended=meta.recommended,
    )

    return OptimizeResponse(
        algorithm=algo_enum.value,
        metadata=meta_dto,
        channel_plans=channel_plans_out,
        simulation=_format_simulation_response(opt_run),
        comparison_with_regulatory={
            "regulatory_npv": round(reg_npv, 2),
            "current_npv": round(cur_npv, 2),
            "delta_npv": delta_npv,
            "savings_pct": savings_pct,
        },
    )
