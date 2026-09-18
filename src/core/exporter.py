"""
Export module for simulation results into standard CSV and Excel (XLSX) workbooks.
Fulfills competition criteria for machine-readable, reproducible deliverables.

Contains complete sheets:
1. Summary_KPI: Comparative metrics between Baseline and Stress
2. Material_Balance: Detailed annual physical flow and inventory trace
3. Economics: Financial decomposition (CAPEX, procurement, reservation, storage, OPEX, NPV)
4. Constraints_Log: Regulatory audit log with explicit PASS/FAIL statuses and diagnostics
All headers include clear units of measurement ([т], [млн у.е.], [%]).
"""

import os
from typing import Dict, List, Optional
import pandas as pd
from src.core.constants import ChannelID
from src.core.scenarios import SimulationRunOutput


def generate_summary_kpi_dataframe(
    baseline: SimulationRunOutput,
    stress: Optional[SimulationRunOutput] = None,
) -> pd.DataFrame:
    """
    Constructs high-level comparative KPI table.
    """
    data = []
    runs = [("Baseline (Номинал)", baseline)]
    if stress:
        runs.append(("Mandatory Stress (Стресс-тест)", stress))

    for label, run in runs:
        b = run.balance
        e = run.economics
        c = run.constraints

        data.append({
            "Сценарий": label,
            "Исполнимость плана [Статус]": "PASS" if c.is_feasible else f"FAIL ({c.total_violations_count} нар.)",
            "Суммарный спрос [т]": round(sum(r.demand_total for r in b.yearly_results.values()), 2),
            "Обслуженный спрос [т]": round(b.total_served_demand, 2),
            "Суммарный дефицит [т]": round(b.total_deficit, 2),
            "Средний уровень общ. сервиса [%]": f"{b.average_service_level_total * 100:.2f}%",
            "Средний уровень крит. сервиса [%]": f"{b.average_service_level_critical * 100:.2f}%",
            "Суммарный валовый приход [т]": round(b.total_gross_delivery, 2),
            "Суммарные потери [т]": round(b.total_losses, 2),
            "Суммарный OPEX [млн у.е.]": round(e.total_opex, 2),
            "Суммарный CAPEX [млн у.е.]": round(e.total_capex, 2),
            "Совокупные расходы (Total Cost) [млн у.е.]": round(e.total_undiscounted_cost, 2),
            "Чистая приведённая стоимость (NPV / LCC) [млн у.е.]": round(e.total_npv_cost, 2),
            "Удельная стоимость обслуженного топлива [млн у.е./т]": round(e.cost_per_ton_served, 4),
            "Дисконтированная стоимость за тонну [млн у.е./т]": round(e.discounted_cost_per_ton_served, 4),
        })

    return pd.DataFrame(data)


def generate_material_balance_dataframe(run: SimulationRunOutput) -> pd.DataFrame:
    """
    Constructs detailed year-by-year physical balance sheet.
    """
    rows = []
    for y, res in sorted(run.balance.yearly_results.items()):
        row = {
            "Год": y,
            "Начальный запас [т]": res.start_stock,
            "Валовый приход суммарно [т]": res.gross_delivery,
        }

        # Per channel inflow
        for ch in ChannelID:
            row[f"Поставка {ch.value} [т]"] = res.channel_deliveries.get(ch, 0.0)

        row.update({
            "Коэффициент потерь [%]": f"{res.throughput_loss_rate * 100:.2f}%",
            "Потери хранения и перекачки [т]": res.losses,
            "Чистый приход топлива [т]": res.net_available_inflow,
            "Всего доступно топлива [т]": res.total_fuel_available,
            "Общий спрос [т/год]": res.demand_total,
            "Критический спрос [т/год]": res.demand_critical,
            "Фактически выдано общее [т]": res.served_demand_total,
            "Фактически выдано крит. [т]": res.served_demand_critical,
            "Общий дефицит [т]": res.deficit_total,
            "Критический дефицит [т]": res.deficit_critical,
            "Конечный запас [т]": res.end_stock,
            "Ёмкость баков хранилища [т]": res.storage_capacity_max,
            "Переполнение ёмкости [т]": res.overflow_amount,
            "Норматив резерва 45 дней [т]": res.required_reserve_45d,
            "Резерв обеспечен физически": "ДА" if res.is_reserve_satisfied_physically else "НЕТ",
            "Уровень сервиса общий [%]": f"{res.service_level_total * 100:.2f}%",
            "Уровень сервиса критический [%]": f"{res.service_level_critical * 100:.2f}%",
        })
        rows.append(row)

    return pd.DataFrame(rows)


def generate_economics_dataframe(run: SimulationRunOutput) -> pd.DataFrame:
    """
    Constructs detailed year-by-year economic and financial sheet.
    """
    rows = []
    for y, econ in sorted(run.economics.yearly_economics.items()):
        row = {
            "Год": y,
            "Закупки суммарно [млн у.е.]": econ.procurement_cost,
            "Резервирование мощностей [млн у.е.]": econ.reservation_cost,
            "Затраты на хранение [млн у.е.]": econ.storage_holding_cost,
            "Фикс. OPEX ZBO [млн у.е.]": econ.zbo_fixed_opex,
            "Фикс. OPEX ISRU [млн у.е.]": econ.isru_fixed_opex,
            "Закупка стартового запаса 2035 [млн у.е.]": econ.initial_stock_acquisition_cost,
            "Итого OPEX [млн у.е.]": econ.total_opex,
            "CAPEX ZBO [млн у.е.]": econ.capex_zbo,
            "CAPEX Earth-New [млн у.е.]": econ.capex_earth_new,
            "CAPEX Lunar-ISRU [млн у.е.]": econ.capex_isru,
            "Итого CAPEX [млн у.е.]": econ.total_capex,
            "Совокупные расходы года [млн у.е.]": econ.total_expenditure,
            "Дисконтный множитель DF (r=8%)": econ.discount_factor,
            "Дисконтированные расходы (NPV) [млн у.е.]": econ.discounted_expenditure,
        }

        # Breakdown by channel
        for ch in ChannelID:
            ch_cost = econ.channel_costs.get(ch)
            if ch_cost:
                row[f"{ch.value}: Бронь [т]"] = ch_cost.reserved_capacity
                row[f"{ch.value}: Заказ [т]"] = ch_cost.ordered_volume
                row[f"{ch.value}: Порог TOP [т]"] = ch_cost.take_or_pay_threshold
                row[f"{ch.value}: Тариф [млн/т]"] = ch_cost.effective_unit_price
                row[f"{ch.value}: Платеж [млн у.е.]"] = ch_cost.total_channel_payment

        rows.append(row)

    return pd.DataFrame(rows)


def generate_constraints_log_dataframe(run: SimulationRunOutput) -> pd.DataFrame:
    """
    Constructs audit log of all constraint checks with explicit PASS/FAIL.
    """
    rows = []
    for c in run.constraints.all_checks:
        rows.append({
            "Год": str(c.year),
            "Код правила": c.rule_code,
            "Наименование ограничения": c.rule_name,
            "Статус": "FAIL" if c.is_violated else "PASS",
            "Требуемое условие": c.expected,
            "Фактическое значение": c.actual,
            "Диагностическое сообщение": c.message,
        })
    return pd.DataFrame(rows)


def export_to_excel(
    baseline_run: SimulationRunOutput,
    stress_run: Optional[SimulationRunOutput] = None,
    output_path: str = "results/fuel_depot_simulation_report.xlsx",
) -> str:
    """
    Exports complete multi-tab verified workbook.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    df_kpi = generate_summary_kpi_dataframe(baseline_run, stress_run)
    df_bal_base = generate_material_balance_dataframe(baseline_run)
    df_econ_base = generate_economics_dataframe(baseline_run)
    df_con_base = generate_constraints_log_dataframe(baseline_run)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_kpi.to_excel(writer, sheet_name="Summary_KPI", index=False)
        df_bal_base.to_excel(writer, sheet_name="Material_Balance_Base", index=False)
        df_econ_base.to_excel(writer, sheet_name="Economics_Base", index=False)
        df_con_base.to_excel(writer, sheet_name="Constraints_Base", index=False)

        if stress_run:
            df_bal_stress = generate_material_balance_dataframe(stress_run)
            df_econ_stress = generate_economics_dataframe(stress_run)
            df_con_stress = generate_constraints_log_dataframe(stress_run)

            df_bal_stress.to_excel(writer, sheet_name="Material_Balance_Stress", index=False)
            df_econ_stress.to_excel(writer, sheet_name="Economics_Stress", index=False)
            df_con_stress.to_excel(writer, sheet_name="Constraints_Stress", index=False)

    return os.path.abspath(output_path)


def export_to_csv(
    run: SimulationRunOutput,
    output_dir: str = "results/csv",
    prefix: str = "baseline",
) -> Dict[str, str]:
    """
    Exports individual sheets into clean CSV files.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    df_bal = generate_material_balance_dataframe(run)
    p_bal = os.path.join(output_dir, f"{prefix}_material_balance.csv")
    df_bal.to_csv(p_bal, index=False, encoding="utf-8-sig")
    generated_files["balance"] = p_bal

    df_econ = generate_economics_dataframe(run)
    p_econ = os.path.join(output_dir, f"{prefix}_economics.csv")
    df_econ.to_csv(p_econ, index=False, encoding="utf-8-sig")
    generated_files["economics"] = p_econ

    df_con = generate_constraints_log_dataframe(run)
    p_con = os.path.join(output_dir, f"{prefix}_constraints_log.csv")
    df_con.to_csv(p_con, index=False, encoding="utf-8-sig")
    generated_files["constraints"] = p_con

    return generated_files
