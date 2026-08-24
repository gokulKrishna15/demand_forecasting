# AI Supply Chain POC — Implementation Plan

**Context:** Proof of concept covering all 3 AI initiatives from the BSL "Disruptive Innovation" workshop memo (Bokaro Niwas, 02.07.2027):
1. AI-based Demand Forecasting
2. AI-based Technical and Commercial Evaluation
3. AI-based Cost Prediction (Ferro Alloys, Raw Materials & Consumables)

**Target:** September 2026 demo readiness.

This document is written to be handed to an agentic coding tool (e.g. Claude Code) as a build spec. Each phase has explicit tasks, file paths, and acceptance criteria so the agent can work through it sequentially and self-verify.

---

## 1. Architecture overview

Two tool tracks feeding one combined dashboard:

- **Track A — Numeric/tabular (H2O-3 AutoML):** serves Demand Forecasting + Cost Prediction
- **Track B — Document/text (RAG + Groq LLM):** serves Technical & Commercial Evaluation
- **Shared layer:** common data directory, common config, common API gateway
- **Presentation layer:** single dashboard with 3 tabs, one per initiative

```
                ┌─────────────────────────────┐
                │        Web Dashboard         │
                │   (3 tabs, 1 per initiative)  │
                └──────────────┬────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │     FastAPI backend  │
                    └──────────┬──────────┘
              ┌─────────────────┴─────────────────┐
     ┌────────┴────────┐                ┌──────────┴─────────┐
     │  Track A: H2O    │                │  Track B: RAG+Groq  │
     │  AutoML models   │                │  retrieval + LLM     │
     └────────┬────────┘                └──────────┬─────────┘
              │                                     │
     ┌────────┴────────┐                ┌──────────┴─────────┐
     │ data/tabular/*.csv│               │ data/docs/*.pdf     │
     └──────────────────┘                └────────────────────┘
```

---

## 2. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| ML engine | H2O-3 (Python, `h2o` package) | AutoML for tabular prediction |
| LLM | Groq API (Llama or Mixtral model) | Fast inference for RAG |
| Embeddings | `sentence-transformers` (local) or Groq-compatible embedding endpoint | Avoid paid embedding API for POC |
| Vector store | ChromaDB (local, file-based) | No external DB dependency for POC |
| Backend | FastAPI | Serves both tracks via REST endpoints |
| Frontend | Simple React or plain HTML/JS dashboard | 3 tabs |
| Data | Kaggle datasets initially, swappable for internal CSVs later | See Phase 1 |
| Deployment | Existing VM infra (self-hosted) | No cloud AI subscription needed for POC |

---

## 3. Repository structure

```
ai-supply-chain-poc/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── tabular/
│   │   ├── cost_prediction_raw.csv
│   │   └── demand_forecast_raw.csv
│   └── docs/
│       └── sample_vendor_bids/          # dummy PDFs for RAG
├── backend/
│   ├── main.py                          # FastAPI app entrypoint
│   ├── config.py                        # env vars, paths
│   ├── track_a_tabular/
│   │   ├── train_cost_model.py
│   │   ├── train_demand_model.py
│   │   ├── predict.py
│   │   └── models/                      # saved H2O model artifacts
│   ├── track_b_rag/
│   │   ├── ingest.py                    # chunk + embed docs into Chroma
│   │   ├── retrieve.py
│   │   ├── groq_client.py
│   │   └── vectorstore/                 # Chroma persistence dir
│   └── api/
│       ├── routes_cost.py
│       ├── routes_demand.py
│       └── routes_eval.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
└── docs/
    └── infra_cost_notes.md              # Phase 8 output
```

---

## 4. Phase-by-phase build plan

### Phase 1 — Environment and data setup
**Goal:** working dev environment, placeholder datasets in place.

Tasks:
- [ ] Create repo structure above
- [ ] `requirements.txt`: `h2o`, `fastapi`, `uvicorn`, `groq`, `chromadb`, `sentence-transformers`, `pypdf`, `pandas`, `python-dotenv`
- [ ] `.env.example` with `GROQ_API_KEY=`, `H2O_MAX_MEM=4G`, `DATA_DIR=./data`
- [ ] Download a Kaggle commodity/raw-material pricing dataset → `data/tabular/cost_prediction_raw.csv`
- [ ] Download a Kaggle demand/sales time-series dataset → `data/tabular/demand_forecast_raw.csv`
- [ ] Create 5-10 dummy vendor bid PDFs (or plain text) → `data/docs/sample_vendor_bids/`
- [ ] `pip install -r requirements.txt --break-system-packages` and verify `h2o.init()` runs without error

**Acceptance criteria:** `python -c "import h2o; h2o.init(); h2o.shutdown()"` succeeds. Both CSVs load with `pandas.read_csv` without errors. At least 5 files exist in `sample_vendor_bids/`.

---

### Phase 2 — Cost Prediction model (Track A, first)
**Goal:** working H2O AutoML model on the pricing dataset with an explainability output.

Tasks:
- [ ] `backend/track_a_tabular/train_cost_model.py`:
  - Load `cost_prediction_raw.csv` into H2O frame
  - Split train/test (80/20)
  - Run `H2OAutoML(max_models=20, seed=1, max_runtime_secs=600)`
  - Save leader model to `backend/track_a_tabular/models/cost_model/`
  - Print leaderboard and variable importance
- [ ] `backend/track_a_tabular/predict.py`: loads saved model, exposes `predict_cost(input_dict) -> {prediction, shap_values}` function
- [ ] `backend/api/routes_cost.py`: `POST /api/cost-prediction` endpoint accepting feature values, returning prediction + top contributing factors

**Acceptance criteria:** running `train_cost_model.py` produces a saved model directory and a leaderboard printout. Hitting `POST /api/cost-prediction` with sample input returns a JSON prediction with at least 3 ranked contributing factors.

---

### Phase 3 — Demand Forecasting model (Track A, extend)
**Goal:** reuse Track A pipeline pattern for the second dataset.

Tasks:
- [ ] `backend/track_a_tabular/train_demand_model.py` — same pattern as Phase 2, pointed at `demand_forecast_raw.csv`. Refactor shared logic (train/save/leaderboard) into a shared helper if duplication is significant.
- [ ] Extend `predict.py` with `predict_demand(input_dict) -> {prediction, shap_values}`
- [ ] `backend/api/routes_demand.py`: `POST /api/demand-forecast` endpoint

**Acceptance criteria:** same as Phase 2, for the demand dataset. Confirm both models can be loaded and queried in the same running process without memory conflicts (single shared `h2o.init()`).

---

### Phase 4 — RAG pipeline (Track B, parallel to Phase 2-3)
**Goal:** working retrieval + LLM answer pipeline over vendor documents.

Tasks:
- [ ] `backend/track_b_rag/ingest.py`:
  - Load PDFs/text from `data/docs/sample_vendor_bids/`
  - Chunk (e.g. 500 tokens, 50 overlap)
  - Embed with `sentence-transformers` (e.g. `all-MiniLM-L6-v2`)
  - Store in ChromaDB at `backend/track_b_rag/vectorstore/`
- [ ] `backend/track_b_rag/retrieve.py`: `retrieve(query, k=5) -> list[chunk]`
- [ ] `backend/track_b_rag/groq_client.py`: wraps Groq chat completion call, takes query + retrieved chunks, returns grounded answer
- [ ] `backend/api/routes_eval.py`: `POST /api/technical-evaluation` endpoint accepting a question (e.g. "which vendor offers the best warranty terms"), returning answer + cited source chunks

**Acceptance criteria:** running `ingest.py` populates the vector store with >0 chunks. A test query against `/api/technical-evaluation` returns an answer referencing at least one source document.

---

### Phase 5 — Minimal interfaces per track
**Goal:** functional (not polished) UI for each track, independently testable.

Tasks:
- [ ] `frontend/index.html` + `app.js`: three simple forms —
  - Cost Prediction: input fields → prediction + factors
  - Demand Forecasting: input fields → prediction + factors
  - Technical Evaluation: query box → answer + sources
- [ ] Each form calls its respective backend endpoint and renders JSON response as readable text

**Acceptance criteria:** all three forms work end-to-end against the running backend from Phases 2-4.

---

### Phase 6 — Combined dashboard
**Goal:** one presentable demo surface.

Tasks:
- [ ] Add tab navigation to `frontend/index.html` (3 tabs: Cost Prediction / Demand Forecasting / Technical Evaluation)
- [ ] Basic styling in `style.css` — doesn't need to be polished, just legible for a stakeholder demo
- [ ] `backend/main.py`: mount all three routers, serve frontend as static files

**Acceptance criteria:** running `uvicorn backend.main:app` and opening the browser shows all 3 tabs working from a single running process.

---

### Phase 7 — Swap in real data (where available)
**Goal:** replace Kaggle/dummy data with internal Petronet/BSL data where accessible.

Tasks:
- [ ] Identify available internal data sources (past purchase orders, price trends, consumption records, past vendor bid documents)
- [ ] Write a data-loading adapter so `train_cost_model.py` / `train_demand_model.py` / `ingest.py` can point at either the Kaggle placeholder or the internal source via a config flag (`DATA_SOURCE=kaggle|internal` in `.env`)
- [ ] Re-run training/ingestion against real data once available
- [ ] Note any data quality issues found (missing fields, inconsistent units, etc.)

**Acceptance criteria:** switching `DATA_SOURCE=internal` in `.env` and re-running Phase 2-4 scripts works without code changes, only data file swaps.

---

### Phase 8 — Cost and infra documentation
**Goal:** input for the C&IT/SDTD evaluation referenced in the original memo.

Tasks:
- [ ] `docs/infra_cost_notes.md` — record:
  - VM specs used (CPU/RAM/storage) and whether existing infra sufficed
  - H2O-3 license cost (should be $0 — open source, Apache 2.0)
  - Groq API usage pattern and any cost incurred during POC (Groq has a free/low-cost tier — note actual usage)
  - Any additional cybersecurity/training needs observed while building
  - Comparison point: what a subscription AI platform would likely have cost vs. this self-hosted approach

**Acceptance criteria:** document exists and covers all bullet points above with actual figures from the build, not estimates.

---

## 5. Environment variables reference (`.env.example`)

```
GROQ_API_KEY=
H2O_MAX_MEM=4G
DATA_DIR=./data
DATA_SOURCE=kaggle
VECTORSTORE_DIR=./backend/track_b_rag/vectorstore
```

---

## 6. Suggested build order for the agent

1. Phase 1 (environment)
2. Phase 2 (Cost Prediction — fastest tangible win)
3. Phase 4 (RAG — independent, can run in parallel/next)
4. Phase 3 (Demand Forecasting — reuses Phase 2 pattern)
5. Phase 5 → Phase 6 (interfaces, then combine)
6. Phase 7 (real data swap, once internal data is available)
7. Phase 8 (documentation, last — needs real usage numbers)

## 7. Out of scope for this POC

- Production-grade authentication/authorization
- Multi-user concurrency handling
- Automated retraining/scheduling
- Formal integration with SAP/existing procurement systems (separate advisory track)
