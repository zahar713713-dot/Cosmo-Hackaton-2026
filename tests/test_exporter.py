"""
Tests for exporter module (CSV and XLSX generation).
"""

import os
import pytest
from src.core.constants import SimulationConfig
from src.core.scenarios import ScenarioType, apply_scenario
from src.core.exporter import (
    export_to_excel,
    export_to_csv,
    generate_summary_kpi_dataframe,
    generate_material_balance_dataframe,
    generate_economics_dataframe,
    generate_constraints_log_dataframe,
)
from tests.test_scenarios import get_base_plan_dict


class TestExporter:
    def test_exporter_excel_and_csv_generation(self, tmp_path):
        config = SimulationConfig(start_year=2035, end_year=2040)
        plans = get_base_plan_dict()

        base_run = apply_scenario(plans, ScenarioType.BASELINE, config)
        stress_run = apply_scenario(plans, ScenarioType.MANDATORY_STRESS, config)

        # 1. Verify DataFrames
        df_kpi = generate_summary_kpi_dataframe(base_run, stress_run)
        assert len(df_kpi) == 2
        assert "Сценарий" in df_kpi.columns
        assert "Исполнимость плана [Статус]" in df_kpi.columns

        df_bal = generate_material_balance_dataframe(base_run)
        assert len(df_bal) == 6
        assert "Начальный запас [т]" in df_bal.columns
        assert "Потери хранения и перекачки [т]" in df_bal.columns

        df_econ = generate_economics_dataframe(base_run)
        assert len(df_econ) == 6
        assert "Итого OPEX [млн у.е.]" in df_econ.columns
        assert "Дисконтированные расходы (NPV) [млн у.е.]" in df_econ.columns

        df_con = generate_constraints_log_dataframe(base_run)
        assert len(df_con) > 0
        assert "Статус" in df_con.columns

        # 2. Verify Excel workbook export
        xlsx_path = str(tmp_path / "test_report.xlsx")
        out_xlsx = export_to_excel(base_run, stress_run, xlsx_path)
        assert os.path.exists(out_xlsx)
        assert os.path.getsize(out_xlsx) > 0

        # 3. Verify CSV export
        csv_dir = str(tmp_path / "csv_out")
        csv_files = export_to_csv(base_run, csv_dir, prefix="baseline")
        assert len(csv_files) == 3
        for k, p in csv_files.items():
            assert os.path.exists(p)
            assert os.path.getsize(p) > 0
