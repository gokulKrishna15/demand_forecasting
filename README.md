# SAIL BSL — SCM AI Innovation Suite

**Proof of Concept** covering 3 AI initiatives from the Bokaro Niwas "Disruptive Innovation in SCM" workshop memo.

> 100% Free & Open-Source · Apache 2.0 · ₹ 0 Licensing Cost

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│       Streamlit Dashboard  (Open-Source, Apache 2.0)      │
│  Tab 1: Overview  |  Tab 2: Demand  |  Tab 3: Tender  |  Tab 4: Cost  │
└──────────────────────┬──────────────────────────┘
                       │ optional REST
          ┌────────────▼────────────┐
          │    FastAPI  backend      │
          │  /api/demand/*           │
          │  /api/cost/*             │
          │  /api/tender/*           │
          └──┬───────────────────┬──┘
             │                   │
   ┌──────────▼──────┐  ┌────────▼───────────┐
   │  H2O-3 AutoML   │  │  TenderEvaluation   │
   │  (h2oai/h2o-3)  │  │  (Rule-based + RAG) │
   │  + sklearn fback │  │  + Groq LLM option  │
   └──────────┬──────┘  └────────────────────┘
              │
   ┌──────────▼──────────┐
   │   data/             │
   │  ├─ bsl_maintenance_spares.csv    │
   │  ├─ bsl_ferro_alloys_market.csv   │
   │  ├─ bsl_tender_rfp.json          │
   │  └─ bsl_vendor_bids.json         │
   └─────────────────────┘
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate synthetic BSL datasets
```bash
python backend/data_generator.py
```

### 3. Run the Streamlit dashboard (primary UI)
```bash
streamlit run streamlit_app.py
```
Opens at **http://localhost:8501**

### 4. (Optional) Run the FastAPI REST backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs at **http://localhost:8000/docs**

### 5. Run tests
```bash
pytest tests/ -v
```

---

## Open-Source Stack

| Layer | Tool | Repo | Licence |
|---|---|---|---|
| ML Engine (primary) | H2O-3 AutoML | [h2oai/h2o-3](https://github.com/h2oai/h2o-3) | Apache 2.0 |
| ML Engine (fallback) | scikit-learn | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | BSD |
| Frontend Dashboard | Streamlit | [streamlit/streamlit](https://github.com/streamlit/streamlit) | Apache 2.0 |
| REST API | FastAPI | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | MIT |
| Charts | Plotly | [plotly/plotly.py](https://github.com/plotly/plotly.py) | MIT |
| RAG Vector DB | ChromaDB | [chroma-core/chroma](https://github.com/chroma-core/chroma) | Apache 2.0 |
| LLM Inference | Groq API | — | Free tier |

---

## Environment Variables (`.env`)

```env
GROQ_API_KEY=          # Required only for Track B RAG/LLM endpoints
H2O_MAX_MEM=4G         # JVM memory for H2O-3 (needs Java 8+)
DATA_DIR=./data
DATA_SOURCE=local       # or 'internal' for real BSL data
```

> **H2O-3 Note:** Requires Java 8+ on the machine. If Java is not installed, the app automatically falls back to scikit-learn — all 4 dashboard tabs will still work.

---

## 3 AI Initiatives

| # | Initiative | Engine | Owner | Target |
|---|---|---|---|---|
| 1 | AI Demand Forecasting (Maintenance Spares) | H2O-3 AutoML | CGM (Maintenance) | Sept 2026 |
| 2 | AI Technical & Commercial Bid Evaluation | Rule-based + Groq RAG | CGM (MM) | Sept 2026 |
| 3 | AI Cost Prediction (Ferro Alloys) | H2O-3 AutoML | CGM (MM) | Sept 2026 |