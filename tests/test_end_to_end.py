import os
import sys
import pytest
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


# ── Pre-flight: ensure data exists ──────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def generate_test_data():
    """Generate synthetic datasets if they don't already exist."""
    from backend.config import (
        MAINTENANCE_DATA_FILE, TENDER_RFP_FILE,
        VENDOR_BIDS_FILE, FERRO_ALLOYS_DATA_FILE,
    )
    from backend.data_generator import (
        generate_large_maintenance_dataset,
        generate_tender_data,
        generate_large_ferro_alloys_market_dataset,
    )
    if not MAINTENANCE_DATA_FILE.exists():
        generate_large_maintenance_dataset()
    if not TENDER_RFP_FILE.exists() or not VENDOR_BIDS_FILE.exists():
        generate_tender_data()
    if not FERRO_ALLOYS_DATA_FILE.exists():
        generate_large_ferro_alloys_market_dataset()


# ── FastAPI client ──────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def api_client(generate_test_data):  # ensure data exists before app import
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# API tests
# ═══════════════════════════════════════════════════════════════════════════
def test_api_health(api_client):
    res = api_client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "SAIL" in data["plant"]


def test_demand_items_endpoint(api_client):
    res = api_client.get("/api/demand/items")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 5
    assert "item_id" in items[0]


def test_demand_forecast_endpoint(api_client):
    # Get first item id
    items = api_client.get("/api/demand/items").json()
    first_id = items[0]["item_id"]

    res = api_client.post("/api/demand/forecast",
                          json={"item_id": first_id, "horizon_months": 6})
    assert res.status_code == 200
    data = res.json()
    assert "future_forecast" in data
    assert len(data["future_forecast"]) == 6
    assert "automl_leaderboard" in data


def test_cost_commodities_endpoint(api_client):
    res = api_client.get("/api/cost/commodities")
    assert res.status_code == 200
    comms = res.json()
    assert len(comms) >= 3
    keys = [c["key"] for c in comms]
    assert "simn" in keys


def test_cost_predict_endpoint(api_client):
    res = api_client.post("/api/cost/predict", json={"commodity_key": "simn"})
    assert res.status_code == 200
    data = res.json()
    corr = data["negotiation_corridor"]
    assert corr["p10_aggressive_offer_inr"] < corr["p50_fair_should_cost_inr"]
    assert corr["p50_fair_should_cost_inr"] < corr["p90_upper_ceiling_inr"]


def test_tender_evaluate_endpoint(api_client):
    res = api_client.get("/api/tender/evaluate")
    assert res.status_code == 200
    data = res.json()
    assert len(data["comparative_statement_of_tenders"]) == 3
    rec = data["executive_purchase_recommendation"]
    assert rec["recommended_rank"] == "L1"


# ═══════════════════════════════════════════════════════════════════════════
# Engine unit tests (direct, no HTTP)
# ═══════════════════════════════════════════════════════════════════════════
def test_demand_forecasting_engine():
    from backend.models.demand_forecasting import DemandForecastingEngine
    engine = DemandForecastingEngine()
    items = engine.get_items_list()
    assert len(items) >= 5

    result = engine.train_and_forecast(items[0]["item_id"], 6)
    assert len(result["future_forecast"]) == 6
    inv = result["inventory_optimization"]
    assert inv["ai_optimized_safety_stock_units"] > 0
    assert inv["reorder_point_units"] > inv["ai_optimized_safety_stock_units"]


def test_tender_evaluation_engine():
    from backend.models.tender_evaluation import TenderEvaluationEngine
    engine = TenderEvaluationEngine()
    result = engine.evaluate_tender()
    cst = result["comparative_statement_of_tenders"]
    assert len(cst) == 3
    rec = result["executive_purchase_recommendation"]
    assert rec["recommended_rank"] == "L1"
    assert "Bharat Heavy Hydraulics" in rec["recommended_vendor"]
    apex = next(v for v in cst if "Apex" in v["vendor_name"])
    assert len(apex["technical_deviations"]) > 0


def test_cost_prediction_engine():
    from backend.models.cost_prediction import FerroAlloysCostPredictionEngine
    engine = FerroAlloysCostPredictionEngine()
    assert len(engine.get_available_commodities()) >= 3

    res = engine.train_and_evaluate("simn")
    corr = res["negotiation_corridor"]
    assert corr["p10_aggressive_offer_inr"] < corr["p50_fair_should_cost_inr"]
    assert corr["p50_fair_should_cost_inr"] < corr["p90_upper_ceiling_inr"]
    assert corr["potential_annual_savings_inr"] > 0


def test_what_if_cost_simulation():
    from backend.models.cost_prediction import FerroAlloysCostPredictionEngine
    engine = FerroAlloysCostPredictionEngine()
    base = engine.train_and_evaluate("fesi")["negotiation_corridor"]["p50_fair_should_cost_inr"]
    sim = engine.train_and_evaluate(
        "fesi", simulated_inputs={"industrial_power_tariff_inr_kwh": 9.50}
    )["negotiation_corridor"]["p50_fair_should_cost_inr"]
    # Higher electricity tariff → higher FeSi cost (~58% power driven)
    assert sim > base
