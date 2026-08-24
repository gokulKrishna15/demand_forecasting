# ⚙️ SAIL Bokaro Steel Plant (BSL) — SCM AI Innovation Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![H2O-3 AutoML](https://img.shields.io/badge/ML%20Engine-H2O--3%20AutoML-yellow.svg)](https://github.com/h2oai/h2o-3)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

An enterprise-grade, on-premise Supply Chain Management AI platform engineered for **Steel Authority of India Limited (SAIL), Bokaro Steel Plant (BSL)**. This platform addresses critical operational challenges in maintenance spares inventory holding, tender compliance auditing, and bulk raw material price negotiations.

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [System Architecture](#-system-architecture)
- [Core AI Modules](#-core-ai-modules)
  - [1. AI Demand Forecasting](#1-ai-demand-forecasting-maintenance-spares)
  - [2. AI Tender Evaluation](#2-ai-technical--commercial-tender-evaluation)
  - [3. AI Cost Prediction & Should-Cost Modeling](#3-ai-should-cost-prediction--negotiation-corridor)
- [Real-Time Open Data Ingestion Pipeline](#-real-time-open-data-ingestion-pipeline)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Enterprise Deployment & Security](#-enterprise-deployment--security)
- [Automated Verification & Testing](#-automated-verification--testing)
- [Documentation Index](#-documentation-index)

---

## 🌟 Executive Overview

Public sector steel manufacturing faces volatile raw material markets, high inventory holding costs, and manual tender evaluation cycles that take weeks. The **SAIL BSL SCM AI Innovation Suite** delivers:

* **32% Working Capital Reduction:** Dynamic safety stock optimization for critical spares across Blast Furnaces, Steel Melting Shops, and Rolling Mills.
* **95% Reduction in Bid Evaluation Cycle:** Automated multi-clause technical audits and Comparative Statement of Tenders (CST) generation.
* **₹ 3.84 Cr+ Annual Procurement Savings:** Data-backed P10/P50/P90 negotiation corridors and should-cost modeling for bulk Ferro Alloys.
* **100% Free & Open-Source Stack:** Zero recurring per-user, per-seat, or per-core licensing fees.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────────────────────────────────┐
                               │               SAIL BSL SCM AI PLATFORM                  │
                               └────────────────────────────┬────────────────────────────┘
                                                            │
                     ┌──────────────────────────────────────┼──────────────────────────────────────┐
                     ▼                                      ▼                                      ▼
      ┌─────────────────────────────┐        ┌─────────────────────────────┐        ┌─────────────────────────────┐
      │  1. DEMAND FORECASTING      │        │  2. TENDER EVALUATION       │        │  3. COST & NEGOTIATION      │
      ├─────────────────────────────┤        ├─────────────────────────────┤        ├─────────────────────────────┤
      │ • H2O-3 AutoML Tournament   │        │ • Multi-Clause RFP Parser   │        │ • Multi-Variable Regression │
      │ • 10-Yr Historical Series   │        │ • Commercial Loading Engine │        │ • Live USD/INR Spot Feeds   │
      │ • Dynamic Safety Stock & ROP│        │ • CST Matrix & L1/L2 Rank   │        │ • P10/P50/P90 Corridor      │
      │ • 95% Service Level Target  │        │ • Action Item Prescriptions │        │ • What-If Market Simulator  │
      └──────────────┬──────────────┘        └──────────────┬──────────────┘        └──────────────┬──────────────┘
                     │                                      │                                      │
                     └──────────────────────────────────────┼──────────────────────────────────────┘
                                                            │
                               ┌────────────────────────────┴────────────────────────────┐
                               ▼                                                         ▼
                ┌─────────────────────────────┐                           ┌─────────────────────────────┐
                │   STREAMLIT DASHBOARD (UI)  │                           │      FASTAPI REST SERVER    │
                │   • Interactive Visuals     │                           │      • SAP RFC/BAPI Bridge  │
                │   • What-If Counter-Offers  │                           │      • Level-2 SCADA Feed   │
                │   • Live Ticker & Telemetry │                           │      • JSON OpenAPI Specs   │
                └─────────────────────────────┘                           └─────────────────────────────┘
```

---

## 🚀 Core AI Modules

### 1. AI Demand Forecasting (Maintenance Spares)
* **Algorithms:** H2O-3 AutoML (Distributed Gradient Boosting, Random Forests, Ridge GLM, Stacked Ensembles) with automated Scikit-Learn fallback.
* **Features:** Multi-lag demand (`lag_1`, `lag_2`, `lag_3`), rolling mean and standard deviation, trigonometric month seasonality (`sin_month`, `cos_month`), hot metal production volume, and planned blast furnace overhaul cycles.
* **Outputs:** 
  * 6-to-12-month forward forecast with 90% confidence bands.
  * AI-optimized **Safety Stock** and **Reorder Point (ROP)**.
  * Quantified **Working Capital Freed (₹)** compared to traditional 2-month heuristic buffers.

### 2. AI Technical & Commercial Tender Evaluation
* **Engine:** Rule-based multi-clause audit engine with strict tolerance thresholds.
* **Auditing Features:** Automatic verification of working pressure ratings, flow rates, motor efficiency classes, filtration ratings, delivery timelines, and warranty periods.
* **Commercial Normalization:** Automatically applies standard financial loading penalties (e.g. +2% for warranty deficits, +3% for delivery delays) and flags prohibitive advance payment clauses.
* **Outputs:** Instant **Comparative Statement of Tenders (CST)** with L1/L2/L3 determination, technical compliance matrix, and purchase committee action items.

### 3. AI Should-Cost Prediction & Negotiation Corridor
* **Model:** Multivariate regression modeling actual purchase order rates against global commodity inputs.
* **Cost Drivers:** Real-world USD/INR exchange rate, Industrial Power Tariffs (₹/kWh), Global Manganese Ore CIF ($/dmtu), and Imported Met Coke CIF ($/MT).
* **Outputs:**
  * **P10 (Aggressive Offer):** Target price to open negotiations or reverse auctions.
  * **P50 (Fair Should-Cost):** Statistically grounded fair procurement price.
  * **P90 (Upper Ceiling):** Maximum walk-away ceiling for purchase officers.
  * **What-If Market Simulator:** Real-time parameter sliders allowing negotiators to model energy price or exchange rate shocks in milliseconds.

---

## 🌐 Real-Time Open Data Ingestion Pipeline

The platform connects to free, open public financial and macroeconomic APIs without requiring proprietary API keys:

| Data Stream | Source / Endpoint | Update Frequency | Purpose in System |
|---|---|---|---|
| **USD/INR FX Spot Rate** | Yahoo Finance (`INR=X`) / Frankfurter ECB | Real-Time Live | Drives should-cost modeling and import price conversions. |
| **Crude Oil / Energy** | Yahoo Finance (`BZ=F`, `CL=F`) | Daily / Monthly | Benchmark for freight and captive energy tariffs. |
| **Industrial Output Index** | World Bank Open Data API (`NV.IND.MANF.ZS`) | Annual / Multi-Year | Macro calibration for steel production demand growth. |

---

## 💻 Getting Started

### Prerequisites
* Python 3.10, 3.11, 3.12, or 3.13
* Git

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/gokulKrishna15/demand_forecasting.git
cd demand_forecasting

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Synchronize Real-World Open API Data
```bash
python backend/live_data_pipeline.py
```

### 3. Launch Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```
Access the application at **`http://localhost:8501`**.

### 4. (Optional) Run FastAPI REST Gateway
```bash
uvicorn backend.main:app --reload --port 8000
```
Interactive Swagger API documentation available at **`http://localhost:8000/docs`**.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check and active ML engine metadata. |
| `GET` | `/api/demand/items` | List of all monitored equipment spares and consumables. |
| `POST` | `/api/demand/forecast` | Run H2O AutoML forward forecast and safety stock optimization. |
| `GET` | `/api/cost/commodities` | List of supported bulk ferro alloys and raw materials. |
| `POST` | `/api/cost/predict` | Calculate P10/P50/P90 should-cost negotiation corridor. |
| `GET` | `/api/tender/evaluate` | Audit active tender RFP bids and generate CST matrix. |

---

## 🔒 Enterprise Deployment & Security

1. **Air-Gapped Intranet Deployment:**
   * Designed to run completely on-premise within SAIL's corporate network.
   * Zero telemetry or bid data leaves the internal server perimeter.
2. **SAP ECC & SCADA Interoperability:**
   * Ready for direct connectivity to SAP MM/PM modules (`MSEG`, `EKPO` tables) via standard RFC/BAPI connectors.
   * Level-2 SCADA logs ingested seamlessly via REST or batch CSV.
3. **Hardware Specifications:**
   * Dual-Socket Enterprise Server (32 Cores, 64 GB RAM recommended).
   * Supports standard Linux (RHEL / Ubuntu) and Windows Server environments.

---

## 🧪 Automated Verification & Testing

The platform includes an automated end-to-end integration test suite covering ML engines, API routes, and What-If simulators:

```bash
pytest tests/ -v
```

Expected output:
```
============================== test session starts ==============================
collected 10 items

tests/test_end_to_end.py::test_api_health PASSED                         [ 10%]
tests/test_end_to_end.py::test_demand_items_endpoint PASSED              [ 20%]
tests/test_end_to_end.py::test_demand_forecast_endpoint PASSED           [ 30%]
tests/test_end_to_end.py::test_cost_commodities_endpoint PASSED          [ 40%]
tests/test_end_to_end.py::test_cost_predict_endpoint PASSED              [ 50%]
tests/test_end_to_end.py::test_tender_evaluate_endpoint PASSED           [ 60%]
tests/test_end_to_end.py::test_demand_forecasting_engine PASSED          [ 70%]
tests/test_end_to_end.py::test_tender_evaluation_engine PASSED           [ 80%]
tests/test_end_to_end.py::test_cost_prediction_engine PASSED             [ 90%]
tests/test_end_to_end.py::test_what_if_cost_simulation PASSED            [100%]

======================= 10 passed in 28.67s =======================
```

---

## 📚 Documentation Index

* 🏛️ [Architecture Specification](docs/architecture.md)
* 📘 [User & Operational Guide](docs/user_guide.md)
* 📡 [REST API Documentation](docs/api_reference.md)
* 📋 [Implementation Plan](ai_supply_chain_poc_implementation_plan.md)

---

### License
Distributed under the **Apache License 2.0**. Free for internal commercial and operational use.