# 🏛️ Enterprise Software Architecture Specification
## SAIL Bokaro Steel Plant — SCM AI Innovation Suite

---

## 1. System Overview

The **SAIL BSL SCM AI Innovation Suite** is engineered with a modular, layered architecture separating:
1. **Presentation Layer (Streamlit UI):** Interactive analytics, reactive charts, and negotiation simulators.
2. **API Gateway Layer (FastAPI):** High-performance async REST endpoints for enterprise ERP / SCADA integration.
3. **Machine Learning & Core Intelligence Layer (H2O-3 AutoML & Scikit-Learn):** Distributed AutoML, feature engineering, inventory optimization, and multi-clause tender auditing.
4. **Data Ingestion Layer (Live Open APIs & SAP Adapters):** Real-time financial feeds (Yahoo Finance, World Bank) and on-premise transactional datasets.

---

## 2. Component Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRESENTATION LAYER                                   │
│                            Streamlit Interactive Dashboard                             │
│       ┌───────────────────────┬───────────────────────┬───────────────────────┐        │
│       │ Executive Overview    │ Demand Forecasting    │ Tender Evaluation     │        │
│       │ Tab 1                 │ Tab 2                 │ Tab 3                 │        │
│       └───────────────────────┴───────────────────────┴───────────────────────┘        │
│       ┌───────────────────────────────────────────────────────────────────────┐        │
│       │ Cost Prediction & Negotiation Simulator (Tab 4)                       │        │
│       └───────────────────────────────────────────────────────────────────────┘        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Python in-memory / REST
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                   API GATEWAY LAYER                                    │
│                         FastAPI (Uvicorn ASGI Engine, Async)                           │
│     /api/demand/items     /api/demand/forecast     /api/cost/predict     /api/tender   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                              INTELLIGENCE & MODEL LAYER                                │
│  ┌───────────────────────────────┐                  ┌───────────────────────────────┐  │
│  │ DemandForecastingEngine       │                  │ FerroAlloysCostPrediction     │  │
│  │ • H2O-3 AutoML (GBM/RF/GLM)   │                  │ • Multivariate Regression     │  │
│  │ • Scikit-learn fallback       │                  │ • P10/P50/P90 Corridor Engine │  │
│  │ • 95% Service Level ROP       │                  │ • What-If Simulation Engine   │  │
│  └───────────────────────────────┘                  └───────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ TenderEvaluationEngine                                                           │  │
│  │ • Multi-Clause Specification Audit & Zero-Tolerance Deviations Rule Engine       │  │
│  │ • Commercial Term Normalization & Penalty Loading Engine                         │  │
│  │ • Comparative Statement of Tenders (CST) L1/L2/L3 Ranking Generator             │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                  DATA INGESTION LAYER                                  │
│  ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │ Real-Time Open Financial Feeds          │  │ Enterprise Transactional Datasets   │  │
│  │ • Yahoo Finance (INR=X, BZ=F)           │  │ • bsl_maintenance_spares.csv        │  │
│  │ • World Bank Open Data API              │  │ • bsl_ferro_alloys_market.csv       │  │
│  │ • Frankfurter ECB Exchange Feed         │  │ • bsl_tender_rfp.json               │  │
│  └─────────────────────────────────────────┘  └─────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Breakdown

### 3.1. Machine Learning Engine (H2O-3 AutoML & Scikit-Learn Fallback)
* **Design Pattern:** Singleton Engine with separate `train_model()` (slow, once per item/session) and `predict()` (fast, live in milliseconds) methods.
* **Algorithm Selection:** H2O-3 AutoML runs a tournament across Gradient Boosting Machines, Distributed Random Forests, Regularized Generalized Linear Models, and Stacked Ensembles.
* **Fallback Guarantee:** If Java runtime environment (JRE) or H2O cluster is initializing or unavailable, the system automatically engages an in-process Scikit-Learn ensemble without service interruption.

### 3.2. Demand Forecasting & Inventory Optimization Pipeline
* **Input Features:**
  * Lagged demand variables: $D_{t-1}, D_{t-2}, D_{t-3}$
  * Rolling 3-month statistics: $\mu_{3\text{m}}, \sigma_{3\text{m}}$
  * Trigonometric calendar seasonality: $\sin(2\pi m / 12), \cos(2\pi m / 12)$
  * Steel production telemetry: Hot metal output (MT), operating hours, scheduled overhaul flags.
* **Safety Stock Formula (95% Service Level):**
  $$SS = Z \cdot \sigma_{\text{demand}} \cdot \sqrt{\frac{L}{30}}$$
  where $Z = 1.645$ (for 95% service level), $\sigma_{\text{demand}}$ is monthly demand standard deviation, and $L$ is vendor lead time in days.
* **Reorder Point (ROP):**
  $$ROP = (\text{Daily Consumption Average} \times L) + SS$$

### 3.3. Tender Evaluation & CST Generation Engine
* **Technical Compliance Score:**
  $$\text{Score} = \left(\frac{\text{Compliant Clauses Count}}{\text{Total Mandatory Specifications Count}}\right) \times 100\%$$
* **Commercial Loading Rules:**
  * Delivery schedule delay: $+3\%$ financial loading for >16 weeks lead time.
  * Warranty deficit: $+2\%$ financial loading for <24 months warranty.
  * Advance payment violations: Automatic disqualification under PSU procurement guidelines.
* **Evaluated Landed Price ($P_{\text{evaluated}}$):**
  $$P_{\text{evaluated}} = P_{\text{quoted}} + \sum \text{Commercial Loadings}$$

### 3.4. Should-Cost Negotiation Corridor Engine
* **Statistical Corridor Formulation:**
  * $\text{P50 (Fair Value)} = \hat{y}$ (Model predicted should-cost)
  * $\text{P10 (Aggressive Opening Bid)} = \hat{y} - 1.28 \cdot \text{RMSE}$
  * $\text{P90 (Upper Ceiling / Walk-Away)} = \hat{y} + 1.28 \cdot \text{RMSE}$

---

## 4. Integration with SAIL Enterprise Infrastructure

```
┌──────────────────────────────────┐            ┌──────────────────────────────────┐
│      SAIL SAP ECC / S4HANA       │            │       PLANT LEVEL-2 SCADA        │
│  • Material Master (MARA/MARC)   │            │  • Blast Furnace Hot Metal Logs  │
│  • Goods Movement (MSEG/MKPF)    │            │  • Caster Speed & Telemetry      │
│  • Purchase Orders (EKKO/EKPO)   │            │  • Mill Outages & Overhauls      │
└────────────────┬─────────────────┘            └────────────────┬─────────────────┘
                 │                                               │
                 │ RFC / BAPI / OData                            │ OPC-UA / Modbus TCP
                 ▼                                               ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           SAIL BSL SCM AI API GATEWAY                            │
│                                (FastAPI Server)                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

1. **SAP ERP Connectivity:**
   * Uses standard PyRFC / OData REST connectors to pull material master data and goods issue history.
2. **Level-2 SCADA Connectivity:**
   * Directly interfaces with plant automation computers via OPC-UA or scheduled batch extracts.
3. **Cybersecurity & Air-Gap Compliance:**
   * Operates 100% on-premise within SAIL's intranet.
   * No proprietary plant data is ever transmitted outside the organization.
