"""
Integration tests for FastAPI endpoints (src/main.py and src/api/routes.py).
Uses Starlette/FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.constants import ChannelID, BASE_DEMAND

client = TestClient(app)


def get_valid_payload(scenario_type: str = "baseline") -> dict:
    """Helper to generate valid sample request payload."""
    channel_plans = {}
    for y in range(2035, 2041):
        d_tot = BASE_DEMAND[y].base_total
        core_cap = min(190.0, d_tot * 0.6)
        flex_cap = min(110.0, max(0.0, (d_tot - core_cap) * 0.7))
        isru_cap = min(120.0, max(0.0, d_tot - core_cap - flex_cap)) if y >= 2038 else 0.0

        channel_plans[y] = {
            ChannelID.EARTH_CORE.value: {"reserved_capacity": core_cap, "target_order_volume": core_cap},
            ChannelID.EARTH_FLEX.value: {"reserved_capacity": flex_cap, "target_order_volume": flex_cap},
            ChannelID.EARTH_NEW.value: {"reserved_capacity": 0.0, "target_order_volume": 0.0},
            ChannelID.LUNAR_ISRU.value: {"reserved_capacity": isru_cap, "target_order_volume": isru_cap},
            ChannelID.EMERGENCY.value: {"reserved_capacity": 20.0, "target_order_volume": 0.0},
        }

    return {
        "scenario_type": scenario_type,
        "investments": {
            "zbo_year": 2036,
            "isru_enabled": True,
            "isru_capex_schedule": {2035: 250.0, 2036: 500.0, 2037: 500.0},
            "earth_new_enabled": False,
        },
        "channel_plans": channel_plans,
        "discount_rate": 0.08,
    }


class TestAPIEndpoints:
    def test_health_and_root(self):
        r_root = client.get("/")
        assert r_root.status_code == 200
        assert r_root.json()["status"] == "OPERATIONAL"

        r_health = client.get("/health")
        assert r_health.status_code == 200
        assert r_health.json()["status"] == "healthy"

    def test_get_defaults(self):
        res = client.get("/api/v1/scenarios/defaults")
        assert res.status_code == 200
        data = res.json()
        assert "channels" in data
        assert "demand" in data
        assert "storage" in data
        assert "mandatory_stress_rules" in data
        assert "limits" in data
        assert ChannelID.EARTH_CORE.value in data["channels"]
        assert "2035" in data["demand"] or 2035 in data["demand"]

    def test_simulate_baseline(self):
        payload = get_valid_payload("baseline")
        res = client.post("/api/v1/simulate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["scenario_type"] == "Baseline"
        assert "summary_kpi" in data
        assert len(data["yearly_balance"]) == 6
        assert len(data["yearly_economics"]) == 6
        assert len(data["violations"]) > 0

    def test_simulate_stress(self):
        payload = get_valid_payload("stress")
        res = client.post("/api/v1/simulate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["scenario_type"] == "Mandatory Stress"
        assert data["summary_kpi"]["total_demand_tons"] > 0

    def test_validation_error_russian_translation(self):
        """Checks Russian error message when order exceeds reservation."""
        payload = get_valid_payload("baseline")
        # Order 100 t with 50 t reservation
        payload["channel_plans"][2035][ChannelID.EARTH_CORE.value] = {
            "reserved_capacity": 50.0,
            "target_order_volume": 100.0,
        }
        res = client.post("/api/v1/simulate", json=payload)
        assert res.status_code == 422
        data = res.json()
        assert data["success"] is False
        assert "не может превышать" in data["details"][0]["message"]

    def test_compare_scenarios(self):
        p1 = get_valid_payload("baseline")
        p2 = get_valid_payload("stress")
        compare_payload = {
            "scenarios": [p1, p2],
            "labels": ["Базовый план", "Стрессовый тест"],
        }
        res = client.post("/api/v1/simulate/compare", json=compare_payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["summary_matrix"]) == 2
        assert len(data["deltas_vs_first"]) == 1
        assert "delta_cost_m_cu" in data["deltas_vs_first"][0]

    def test_export_xlsx(self):
        payload = get_valid_payload("baseline")
        res = client.post("/api/v1/export/xlsx", json=payload)
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert len(res.content) > 0

    def test_export_csv(self):
        payload = get_valid_payload("baseline")
        res = client.post("/api/v1/export/csv", json=payload)
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/zip"
        assert len(res.content) > 0

    def test_sensitivity_analysis(self):
        payload = {
            "base_request": get_valid_payload("baseline"),
            "price_shock_range": [-0.10, 0.0, 0.20],
            "demand_shock_range": [-0.10, 0.0, 0.10],
            "isru_delay_years": [0, 1],
        }
        res = client.post("/api/v1/stress/sensitivity", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["tornado_points"]) > 0
        assert "launch_price_elasticity" in data["cost_elasticities"]
        assert "demand_elasticity" in data["cost_elasticities"]

    def test_geopolitical_shock(self):
        payload = {
            "base_request": get_valid_payload("baseline"),
            "start_year": 2037,
            "end_year": 2039,
            "earth_core_price_multiplier": 1.40,
            "earth_flex_price_multiplier": 1.45,
            "description": "Эскалация санкционных ограничений на экспорт КРТ.",
        }
        res = client.post("/api/v1/geopolitical-shock", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "simulation_result" in data
        assert "cost_delta_vs_baseline" in data
        assert "narrative_impact" in data
        assert data["cost_delta_vs_baseline"] > 0
