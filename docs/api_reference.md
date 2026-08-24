# 📡 REST API Reference Specification
## SAIL Bokaro Steel Plant — SCM AI Innovation Suite

The backend provides a high-performance REST API built on **FastAPI**. All requests and responses use standard JSON encoding.

**Base URL:** `http://localhost:8000`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`

---

## 1. System Health

### `GET /health`
Returns system status, active ML engine metadata, and connected datasets.

#### Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "platform": "SAIL Bokaro Steel Plant — SCM AI Innovation Suite",
  "frontend": "Streamlit (open-source)",
  "license": "100% Free & Open-Source (Apache 2.0)",
  "ml_engines": {
    "demand_forecasting": "Operational (H2O-3 AutoML)",
    "tender_evaluation": "Operational (Document AI / Rule-Based)",
    "cost_prediction": "Operational (H2O-3 Regression)"
  }
}
```

---

## 2. Demand Forecasting Endpoints

### `GET /api/demand/items`
Returns the catalog of all monitored equipment spares and consumables.

#### Response:
```json
{
  "total_items": 12,
  "items": [
    {
      "item_id": "SP-BF-001",
      "item_name": "Tuyere Cooler Assembly",
      "department": "Blast Furnace",
      "category": "Mechanical Spares",
      "criticality": "HIGH (A)",
      "unit_cost_inr": 85000.0,
      "lead_time_days": 45
    }
  ]
}
```

---

### `POST /api/demand/forecast`
Generates a multi-month forward forecast, safety stock recommendation, and reorder point.

#### Request Body:
```json
{
  "item_id": "SP-BF-001",
  "horizon_months": 6
}
```

#### Response:
```json
{
  "item_id": "SP-BF-001",
  "horizon_months": 6,
  "engine_used": "H2O-3 AutoML",
  "best_model": "GBM_1_AutoML",
  "item_metadata": {
    "item_name": "Tuyere Cooler Assembly",
    "department": "Blast Furnace",
    "unit_cost_inr": 85000.0,
    "lead_time_days": 45
  },
  "inventory_optimization": {
    "ai_optimized_safety_stock_units": 14,
    "reorder_point_units": 38,
    "traditional_heuristic_buffer_units": 22,
    "inventory_reduction_units": 8,
    "working_capital_freed_inr": 680000,
    "service_level_target": "95.0%"
  },
  "future_forecast": [
    {
      "month_index": 1,
      "date": "2026-09-30",
      "month_str": "Sep 2026",
      "forecast_demand": 16.2,
      "confidence_lower": 13.1,
      "confidence_upper": 19.3,
      "estimated_procurement_cost_inr": 1377000,
      "is_planned_shutdown": 0
    }
  ]
}
```

---

## 3. Ferro Alloys Should-Cost Endpoints

### `GET /api/cost/commodities`
Returns the list of supported bulk raw materials and ferro alloys.

#### Response:
```json
{
  "commodities": [
    {
      "key": "silico_manganese",
      "name": "Silico Manganese (SiMn 60/14)",
      "base_unit": "INR/MT",
      "primary_cost_drivers": ["usd_inr_rate", "industrial_power_tariff_inr_kwh", "mn_ore_cif_usd_dmtu", "imported_coke_cif_usd_mt"]
    }
  ]
}
```

---

### `POST /api/cost/predict`
Calculates the statistical P10/P50/P90 should-cost negotiation corridor.

#### Request Body:
```json
{
  "commodity_key": "silico_manganese",
  "usd_inr_rate": 86.5,
  "industrial_power_tariff_inr_kwh": 6.85,
  "mn_ore_cif_usd_dmtu": 245.0,
  "imported_coke_cif_usd_mt": 360.0
}
```

#### Response:
```json
{
  "commodity_key": "silico_manganese",
  "commodity_name": "Silico Manganese (SiMn 60/14)",
  "negotiation_corridor": {
    "p10_aggressive_counter_inr_mt": 72450.0,
    "p50_fair_should_cost_inr_mt": 76800.0,
    "p90_upper_ceiling_inr_mt": 81150.0,
    "std_error_inr_mt": 3398.4
  },
  "annual_savings_opportunity_inr": 38400000
}
```

---

## 4. Tender Evaluation Endpoints

### `GET /api/tender/evaluate`
Performs an automated multi-clause technical audit, applies commercial loadings, and generates the Comparative Statement of Tenders (CST).

#### Response:
```json
{
  "tender_rfp_summary": {
    "tender_id": "SAIL/BSL/MM/PUR/2026/089",
    "title": "High-Pressure Descaling Hydraulic Power Pack for HSM-2",
    "estimated_budget_inr": 48500000
  },
  "comparative_statement_of_tenders": [
    {
      "rank": "L1",
      "vendor_name": "Bharat Heavy Hydraulics Pvt Ltd",
      "quoted_price_inr": 43500000,
      "commercial_loading_inr": 0,
      "evaluated_landing_price_inr": 43500000,
      "overall_status": "QUALIFIED",
      "technical_score_pct": 100.0
    }
  ],
  "executive_purchase_recommendation": {
    "recommended_vendor": "Bharat Heavy Hydraulics Pvt Ltd",
    "recommended_rank": "L1",
    "order_value_inr": 43500000,
    "savings_against_budget_inr": 5000000
  }
}
```
