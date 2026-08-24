"""
SAIL BSL SCM AI Innovation Suite — Streamlit Dashboard
=======================================================
Open-source frontend powered by Streamlit (github.com/streamlit/streamlit, Apache 2.0).

Architecture
------------
  Engines (DemandForecastingEngine, FerroAlloysCostPredictionEngine) are loaded
  once via @st.cache_resource.

  Model artifacts (trained weights) are stored in st.session_state keyed by
  item_id / commodity_key.  Training only happens on first selection.

  Predictions (forecast, P10/P50/P90 corridor) are called on EVERY rerun —
  they are millisecond-fast because they just call the stored model's predict().

Run:  streamlit run streamlit_app.py
"""

import sys
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from backend.live_market_data import fetch_live_market_bundle, fetch_live_usd_inr
from backend.live_data_pipeline import sync_all_real_world_apis

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
logging.basicConfig(level=logging.WARNING)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAIL BSL — SCM AI Suite",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar (scoped styling) ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 { color: #f1f5f9; }

/* ── Labels for Inputs ── */
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

/* ── Selectbox Container & Inputs (High-Contrast Text) ── */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
}

/* Visible text inside the selectbox input */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] div[data-baseweb="select"] input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 500 !important;
}

/* Dropdown Arrow */
div[data-testid="stSelectbox"] svg {
    fill: #cbd5e1 !important;
}

/* ── Dropdown Popover / Menu Options ── */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li,
li[role="option"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
}

div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover,
li[role="option"]:hover {
    background-color: #334155 !important;
    color: #38bdf8 !important;
    -webkit-text-fill-color: #38bdf8 !important;
}

li[aria-selected="true"] {
    background-color: #1e3a8a !important;
    color: #60a5fa !important;
    -webkit-text-fill-color: #60a5fa !important;
    font-weight: 600 !important;
}

/* ── Button Styling (fixes invisible button text) ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}
div[data-testid="stButton"] button p,
div[data-testid="stButton"] button span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    border-color: #60a5fa !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
}
div[data-testid="stButton"] button:hover p,
div[data-testid="stButton"] button:hover span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ── Radio Controls & Labels ── */
div[data-testid="stRadio"] label {
    color: #cbd5e1 !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p,
div[data-testid="stRadio"] div[role="radiogroup"] label span {
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}

/* ── Live Ticker Badge ── */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10b981;
    color: #34d399;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.live-dot {
    width: 7px;
    height: 7px;
    background-color: #10b981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.2); }
    100% { opacity: 1; transform: scale(1); }
}

/* ── Main background ── */
.main { background: #0f172a; }
.block-container { padding-top: 1.5rem; }

/* ── KPI card ── */
.kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155; border-radius: 12px;
    padding: 1.2rem 1.5rem; text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
.kpi-label { font-size: 0.72rem; font-weight: 500; color: #64748b;
             text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9;
             margin: 0.3rem 0 0; line-height: 1.15; }
.kpi-sub   { font-size: 0.75rem; color: #22d3ee; margin-top: 0.2rem; }

/* ── Section heading ── */
.section-title {
    font-size: 1.05rem; font-weight: 600; color: #38bdf8;
    border-left: 3px solid #3b82f6; padding-left: 0.6rem;
    margin: 1.4rem 0 0.8rem;
}

/* ── Status badges ── */
.badge-ok   { background:#064e3b; color:#34d399; border-radius:6px;
              padding:2px 10px; font-size:0.75rem; font-weight:600; }
.badge-warn { background:#451a03; color:#fb923c; border-radius:6px;
              padding:2px 10px; font-size:0.75rem; font-weight:600; }
.badge-bad  { background:#450a0a; color:#f87171; border-radius:6px;
              padding:2px 10px; font-size:0.75rem; font-weight:600; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:#0f172a; border-bottom:1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { color:#64748b; font-weight:500; }
.stTabs [aria-selected="true"] { color:#38bdf8 !important; border-bottom:2px solid #38bdf8; }

/* ── Misc ── */
.js-plotly-plot .plotly .modebar { background:transparent !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── UI helpers ───────────────────────────────────────────────────────────────
def kpi(label, value, sub=""):
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{"<div class=kpi-sub>" + sub + "</div>" if sub else ""}'
        f"</div>",
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ── Live Market Data State ───────────────────────────────────────────────────
if "live_market_data" not in st.session_state:
    with st.spinner("🌐 Fetching real-time market data (USD/INR FX & Energy indices)…"):
        st.session_state["live_market_data"] = fetch_live_market_bundle()

live_data = st.session_state["live_market_data"]


# ── Load engines once ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️  Loading AI engines…")
def load_engines():
    from backend.data_generator import (
        generate_large_maintenance_dataset,
        generate_tender_data,
        generate_large_ferro_alloys_market_dataset,
    )
    from backend.config import (
        MAINTENANCE_DATA_FILE, TENDER_RFP_FILE,
        VENDOR_BIDS_FILE, FERRO_ALLOYS_DATA_FILE,
    )
    from backend.models.demand_forecasting import DemandForecastingEngine
    from backend.models.tender_evaluation import TenderEvaluationEngine
    from backend.models.cost_prediction import FerroAlloysCostPredictionEngine

    if not MAINTENANCE_DATA_FILE.exists():
        generate_large_maintenance_dataset()
    if not TENDER_RFP_FILE.exists() or not VENDOR_BIDS_FILE.exists():
        generate_tender_data()
    if not FERRO_ALLOYS_DATA_FILE.exists():
        generate_large_ferro_alloys_market_dataset()

    return (
        DemandForecastingEngine(),
        TenderEvaluationEngine(),
        FerroAlloysCostPredictionEngine(),
    )


demand_engine, tender_engine, cost_engine = load_engines()


# ── Model artifact helpers (train once, stored in session_state) ─────────────
def get_demand_artifacts(item_id: str) -> dict:
    key = f"demand_model__{item_id}"
    if key not in st.session_state:
        with st.spinner(f"🔧 Training H2O-3 AutoML model for '{item_id}'… (once per item)"):
            st.session_state[key] = demand_engine.train_model(item_id)
    return st.session_state[key]


def get_cost_artifacts(comm_key: str) -> dict:
    key = f"cost_model__{comm_key}"
    if key not in st.session_state:
        with st.spinner(f"🔧 Training H2O-3 model for '{comm_key}'… (once per commodity)"):
            st.session_state[key] = cost_engine.train_model(comm_key)
    return st.session_state[key]


# ── Header with Live Ticker ──────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(90deg,#1e3a5f 0%,#0f172a 100%);
     padding:1.2rem 1.8rem;border-radius:12px;margin-bottom:1rem;
     border:1px solid #1e40af;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
  <div>
    <h1 style="margin:0;font-size:1.55rem;color:#f1f5f9;font-weight:700;">
      ⚙️ SAIL Bokaro Steel Plant &nbsp;|&nbsp; SCM AI Innovation Suite
    </h1>
    <p style="margin:0.3rem 0 0;font-size:0.82rem;color:#94a3b8;">
      Materials Management &amp; Maintenance Departments
    </p>
  </div>
  <div style="text-align:right;">
    <div class="live-badge">
      <span class="live-dot"></span>
      LIVE FX: USD/INR ₹{live_data['usd_inr']:.2f}
    </div>
    <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">
      Feed: {live_data['source']} ({live_data['timestamp']})
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Global Sidebar Controls ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌐 Live Open Data Feeds")
    st.caption("Real-world live open financial & commodity APIs")
    if st.button("⚡ Ingest Live Open API Data", use_container_width=True, help="Pulls latest real-world series from Yahoo Finance (INR=X, BZ=F) and World Bank Open API"):
        with st.spinner("🌐 Synchronizing real-world open data APIs…"):
            res = sync_all_real_world_apis()
            st.session_state["live_market_data"] = fetch_live_market_bundle()
            demand_engine.load_data()
            cost_engine.load_data()
            # Clear model caches to train on fresh real-world data
            for k in list(st.session_state.keys()):
                if k.startswith("demand_model__") or k.startswith("cost_model__"):
                    del st.session_state[k]
            st.success("✅ Real-world API data synced through Aug 2026!")
            st.rerun()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_demand, tab_tender, tab_cost = st.tabs([
    "📊 Executive Overview",
    "📦 1 · AI Demand Forecasting",
    "📄 2 · AI Tender Evaluation",
    "💰 3 · Ferro Alloys Cost Prediction",
])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown("### Disruptive Innovation in Supply Chain Management — Initiative Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("SCM AI Initiatives", "3 Use Cases", "Operational")
    with c2: kpi("Annual Value Potential", "₹ 8.64 Cr+", "Identified savings")
    with c3: kpi("Software Licensing", "₹ 0.00", "Zero Recurring Fees")
    with c4: kpi("Deployment Model", "On-Premise", "Air-gapped intranet")

    section("Initiative Roadmap")
    initiatives = pd.DataFrame([
        {"Initiative": "AI-based Demand Forecasting",
         "Department": "CGM (Maintenance)",
         "Platform Engine": "H2O-3 (AutoML)",
         "Status": "✅ Operational",
         "Key Metric": "32% Working Capital Reduction"},
        {"Initiative": "AI-based Technical & Commercial Bid Evaluation",
         "Department": "CGM (Materials Management)",
         "Platform Engine": "Document AI / NLP",
         "Status": "✅ Operational",
         "Key Metric": "100% Automated Compliance Audit"},
        {"Initiative": "AI-based Cost Prediction (Ferro Alloys)",
         "Department": "CGM (Materials Management)",
         "Platform Engine": "H2O-3 (Regression)",
         "Status": "✅ Operational",
         "Key Metric": "₹ 3.84 Cr/yr Negotiation Savings"},
    ])
    st.dataframe(initiatives, use_container_width=True, hide_index=True)

    section("Technical Guidance Report for C&IT (BSL) & SDTD (Ranchi)")
    col_l, col_r = st.columns(2)
    with col_l:
        st.info("**Q1 — AI Tools & Platforms**\n\n"
                "• **h2oai/h2o-3** — Distributed AutoML for time-series forecasting & commodity regression\n"
                "• **h2oai/h2ogpt** — Private, local LLM/RAG for tender clause compliance verification\n"
                "• **Streamlit** — Open-source ML dashboard (Apache 2.0)")
        st.info("**Q3 — Licensing & Recurring Cost**\n\n"
                "₹ 0.00 recurring licence cost. Built entirely on free Apache 2.0 open-source "
                "software. Zero per-user or per-model subscription fees.")
    with col_r:
        st.info("**Q2 — Compatibility with SAIL/BSL Systems**\n\n"
                "• SAP ECC 6.0 / S/4HANA — RFC/BAPI connectors or OData REST\n"
                "• Plant Level-2 SCADA & MES — batch & real-time telemetry ingestion\n"
                "• Deployable on SAIL internal Kubernetes or on-premise Linux VMs")
        st.info("**Q4 — Cybersecurity & Infrastructure**\n\n"
                "• **Air-Gapped Intranet** — 100% on-premise within SAIL firewall\n"
                "• **Hardware** — Dual-socket server (32 Cores, 64 GB RAM)\n"
                "• **Training** — 3-day workshop for MM officers & maintenance planners")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — DEMAND FORECASTING
# ═══════════════════════════════════════════════════════════════════════════
with tab_demand:
    demand_engine.load_data()  # Ensure latest real-world data is loaded
    items_list = demand_engine.get_items_list()
    item_options = {f"{i['item_name']} ({i['department']})": i["item_id"] for i in items_list}

    # ── In-Tab Quick Selection Bar ───────────────────────────────────────────
    c_sel1, c_sel2 = st.columns([3, 2])
    with c_sel1:
        selected_label = st.selectbox(
            "📦 Monitored Spare Part / Equipment Subsystem:",
            list(item_options.keys()),
            key="demand_item_main",
            help="Select any spare part to instantly run the H2O-3 forecast."
        )
    with c_sel2:
        horizon = st.slider(
            "📅 Forward Forecast Horizon (Months from Sep 2026):",
            3, 12, 6, key="horizon_main"
        )

    selected_id = item_options[selected_label]

    # ── TRAIN once (if not already in session_state for this item) ───────────
    artifacts = get_demand_artifacts(selected_id)

    # ── PREDICT live — runs every time selection changes (milliseconds) ──────
    forecast_result = demand_engine.predict_future(artifacts, horizon)

    meta = artifacts["item_metadata"]
    inv = artifacts["inventory_optimization"]
    future = forecast_result["future_forecast"]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Criticality", meta["criticality"], meta["category"])
    with c2: kpi("AI Safety Stock", f"{inv['ai_optimized_safety_stock_units']} units",
                 f"Vs {inv['traditional_heuristic_buffer_units']} traditional")
    with c3: kpi("Reorder Point", f"{inv['reorder_point_units']} units", "95% service level")
    with c4: kpi("Working Capital Freed", f"₹ {inv['working_capital_freed_inr']:,}",
                 f"{inv['inventory_reduction_units']} units freed")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        section("AI Demand Forecast Chart")
        import plotly.graph_objects as go

        hist = pd.DataFrame(artifacts["recent_historical_demand"])
        hist["date"] = pd.to_datetime(hist["date"])
        fc_df = pd.DataFrame(future)
        fc_df["date"] = pd.to_datetime(fc_df["date"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist["date"], y=hist["actual_consumption"],
            name="Historical Consumption",
            line=dict(color="#94a3b8", width=2), mode="lines+markers", marker=dict(size=5),
        ))
        fig.add_trace(go.Scatter(
            x=fc_df["date"], y=fc_df["forecast_demand"],
            name="H2O Forecast", line=dict(color="#3b82f6", width=2.5),
            mode="lines+markers", marker=dict(size=7, symbol="circle"),
        ))
        fig.add_trace(go.Scatter(
            x=pd.concat([fc_df["date"], fc_df["date"].iloc[::-1]]),
            y=pd.concat([fc_df["confidence_upper"], fc_df["confidence_lower"].iloc[::-1]]),
            fill="toself", fillcolor="rgba(59,130,246,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="90% Prediction Interval",
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            legend=dict(orientation="h", y=-0.15),
            margin=dict(l=10, r=10, t=10, b=10), height=310,
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b", title="Consumption (Units)"),
        )
        st.plotly_chart(fig, use_container_width=True)

        section("Monthly Procurement Schedule")
        fc_table = pd.DataFrame([{
            "Month": f["month_str"],
            "Forecast Demand": f"{f['forecast_demand']} units",
            "P10 (Min)": f"{f['confidence_lower']} units",
            "P90 (Max)": f"{f['confidence_upper']} units",
            "Est. Cost": f"₹ {f['estimated_procurement_cost_inr']:,}",
            "Plant Schedule": "🔧 Overhaul" if f["is_planned_shutdown"] else "▶ Normal",
        } for f in future])
        st.dataframe(fc_table, use_container_width=True, hide_index=True)

    with col_right:
        section("Item Details")
        st.markdown(f"""
| Field | Value |
|---|---|
| **Item Code** | `{meta['item_id']}` |
| **Department** | {meta['department']} |
| **Unit Cost** | ₹ {meta['unit_cost_inr']:,.0f} |
| **Lead Time** | {meta['lead_time_days']} days |
""")

        section("AutoML Leaderboard")
        lb_df = pd.DataFrame(artifacts["automl_leaderboard"])[
            ["model_id", "rmse", "mape_percent", "r2_score"]]
        lb_df.columns = ["Model", "RMSE", "MAPE %", "R²"]
        lb_df["Model"] = lb_df["Model"].str.replace("H2O_", "").str.replace("_", " ")
        st.dataframe(lb_df, use_container_width=True, hide_index=True)

        section("Feature Importance")
        fi_df = pd.DataFrame(artifacts["feature_importance"])[["feature", "importance_pct"]]
        fi_df.columns = ["Feature", "Importance %"]
        fi_df["Feature"] = fi_df["Feature"].str.replace("_", " ").str.title()
        import plotly.express as px
        fig_fi = px.bar(fi_df, x="Importance %", y="Feature", orientation="h",
                        color="Importance %", color_continuous_scale="Blues")
        fig_fi.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=220,
        )
        st.plotly_chart(fig_fi, use_container_width=True)
        st.caption(f"Engine: `{artifacts['engine_used']}`")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — TENDER EVALUATION
# ═══════════════════════════════════════════════════════════════════════════
with tab_tender:
    packages = tender_engine.get_available_packages()
    pkg_options = {p["name"]: p["key"] for p in packages}

    c_pkg, c_mode = st.columns([3, 2])
    with c_pkg:
        selected_pkg_name = st.selectbox(
            "📋 Select Active Tender RFP Package:",
            list(pkg_options.keys()),
            key="tender_package_sel",
            help="Switch between different SAIL BSL procurement packages."
        )
    with c_mode:
        negotiate_mode = st.checkbox(
            "🛠️ Live Bid Negotiation & Counter-Offer Simulator",
            value=False,
            key="tender_negotiate_mode",
            help="Simulate reverse auctions, price discounts, or deviation waivers."
        )

    pkg_key = pkg_options[selected_pkg_name]
    price_mods = {}
    waive_mods = {}

    if negotiate_mode:
        with st.expander("💼 Live Commercial Negotiation & Counter-Offer Bar", expanded=True):
            st.caption("Adjust vendor bids to simulate price negotiations, counter-offers, or post-TNC deviation clearances:")
            col_n1, col_n2, col_n3 = st.columns(3)
            with col_n1:
                st.markdown("**Bharat Heavy Hydraulics**")
                bh_disc = st.slider("Price Discount %", 0, 20, 0, key="bh_disc")
                price_mods["VEND-IND-0104"] = 1.0 - (bh_disc / 100.0)
            with col_n2:
                st.markdown("**Apex Fluid Power**")
                ap_disc = st.slider("Price Discount %", 0, 25, 0, key="ap_disc")
                price_mods["VEND-IND-0219"] = 1.0 - (ap_disc / 100.0)
                waive_mods["VEND-IND-0219"] = st.checkbox("Clear Technical Deviations", key="ap_waive", help="Check if vendor agrees to comply with 210 bar spec and standard payment terms")
            with col_n3:
                st.markdown("**Hydrowerk GmbH (OEM)**")
                hw_disc = st.slider("Price Discount %", 0, 25, 0, key="hw_disc")
                price_mods["VEND-GER-0881"] = 1.0 - (hw_disc / 100.0)

    with st.spinner("Running AI multi-clause compliance audit & CST ranking…"):
        t_res = tender_engine.evaluate_tender(
            package_key=pkg_key,
            price_modifiers=price_mods if negotiate_mode else None,
            resolve_deviations=waive_mods if negotiate_mode else None,
        )

    rfp = t_res["tender_rfp_summary"]
    rec = t_res["executive_purchase_recommendation"]
    cst = t_res["comparative_statement_of_tenders"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Tender Budget", f"₹ {rfp['estimated_budget_inr']/1e7:.2f} Cr", rfp["tender_id"])
    with c2: kpi("Recommended L1", rec["recommended_rank"],
                 rec["recommended_vendor"][:28] + "…")
    with c3: kpi("Award Value", f"₹ {rec['order_value_inr']/1e7:.2f} Cr",
                 f"{rec['budget_utilization_pct']}% budget utilisation")
    with c4: kpi("Savings vs Budget",
                 f"₹ {rec['savings_against_budget_inr']/1e5:.1f} Lakhs", "Direct procurement saving")

    st.success(f"**Purchase Committee Recommendation:** {rec['justification']}")

    section("Comparative Statement of Tenders (CST)")
    status_map = {
        "QUALIFIED": "✅ QUALIFIED",
        "REJECTED (Technical Deviations)": "❌ REJECTED (Technical Deviations)",
        "DISQUALIFIED (Commercial Policy Violation)": "⚠️ DISQUALIFIED (Policy Violation)",
    }
    cst_df = pd.DataFrame([{
        "Rank": v["rank"],
        "Vendor": v["vendor_name"],
        "Origin": v["vendor_origin"].split("(")[-1].replace(")", ""),
        "Quoted (₹)": f"{v['quoted_price_inr']:,}",
        "Tech Score": f"{v['technical_score_pct']}%",
        "Commercial Loading": f"+ {v['commercial_loading_inr']:,}",
        "Evaluated Price (₹)": f"{v['evaluated_landing_price_inr']:,}",
        "Status": status_map.get(v["overall_status"], v["overall_status"]),
    } for v in cst])
    st.dataframe(cst_df, use_container_width=True, hide_index=True)

    section("Clause-by-Clause Technical Compliance Matrix")
    vendor_names = [v["vendor_name"].split("(")[0].strip()[:20] for v in cst]
    spec_rows = []
    for idx, spec in enumerate(rfp["mandatory_technical_specs"]):
        row = {"Spec": spec["parameter"],
               "Mandatory Requirement": spec["required_value"][:45],
               "Criticality": spec["criticality"]}
        for vi, v in enumerate(cst):
            compliance = v["full_technical_responses"][idx]["compliance"]
            if "Superior" in compliance:
                icon = "🟢 SUPERIOR"
            elif "Non-Compliant" in compliance or "Deviation" in compliance:
                icon = "🔴 DEVIATION"
            elif "Partial" in compliance:
                icon = "🟡 PARTIAL"
            else:
                icon = "✅ COMPLIANT"
            row[vendor_names[vi]] = icon
        spec_rows.append(row)
    st.dataframe(pd.DataFrame(spec_rows), use_container_width=True, hide_index=True)

    section("Action Items for Purchase Committee")
    for item in rec.get("action_items", []):
        st.markdown(f"• {item}")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — FERRO ALLOYS COST PREDICTION
# ═══════════════════════════════════════════════════════════════════════════
with tab_cost:
    commodities = cost_engine.get_available_commodities()
    comm_options = {c["name"]: c["key"] for c in commodities}

    # ── Sidebar controls ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💰 Cost Prediction & Market Feeds")
        selected_comm_name = st.selectbox(
            "Commodity / Alloy", list(comm_options.keys()), key="cost_commodity")
        
        feed_mode = st.radio(
            "Data Feed Mode",
            ["🟢 Real-Time Live Feed", "🛠️ Custom What-If Simulator"],
            index=0,
            key="feed_mode",
            help="Switch between live financial market feeds and manual scenario simulation."
        )

        if feed_mode == "🟢 Real-Time Live Feed":
            st.caption(f"⚡ Connected to {live_data['source']}")
            if st.button("🔄 Sync Live Market Rates", use_container_width=True):
                st.session_state["live_market_data"] = fetch_live_market_bundle()
                st.rerun()
            
            # Live calibrated parameters
            cur_fx = live_data["usd_inr"]
            cur_diesel = live_data["diesel_price_inr_litre"]
            cur_mn_ore = live_data["mn_ore_cif_usd_dmtu"]
            cur_coke = live_data["imported_coke_cif_usd_mt"]
            cur_power = live_data["industrial_power_tariff_inr_kwh"]
            
            st.markdown(f"""
            <div style="background:#1e293b;padding:10px 12px;border-radius:8px;border:1px solid #334155;font-size:0.8rem;color:#cbd5e1;margin-top:6px;">
              <div>• <b>Live USD/INR:</b> <span style="color:#34d399;">₹ {cur_fx:.2f}</span></div>
              <div>• <b>Live Diesel Ref:</b> ₹ {cur_diesel:.2f}/L</div>
              <div>• <b>Live Mn Ore Index:</b> ${cur_mn_ore:.1f}/dmtu</div>
              <div>• <b>Live Met Coke Index:</b> ${cur_coke:.1f}/MT</div>
            </div>
            """, unsafe_allow_html=True)
            
            power = cur_power
            mn_ore = cur_mn_ore
            coke = cur_coke
            usd_inr = cur_fx
        else:
            st.caption("⚡ Modify parameters below for instant What-If negotiation scenarios")
            power   = st.slider("Power Tariff (₹/kWh)",  5.0,  10.0, 6.85, 0.05, key="power")
            mn_ore  = st.slider("Mn Ore CIF ($/dmtu)",   150,   400,  int(live_data["mn_ore_cif_usd_dmtu"]),    5,  key="mn_ore")
            coke    = st.slider("Met Coke CIF ($/MT)",   200,   600,  int(live_data["imported_coke_cif_usd_mt"]),   10,  key="coke")
            usd_inr = st.slider("USD/INR Exchange (₹)",  75.0,  105.0, float(live_data["usd_inr"]), 0.1,  key="usd_inr")

    comm_key = comm_options[selected_comm_name]

    # ── TRAIN once per commodity ──────────────────────────────────────────────
    cost_artifacts = get_cost_artifacts(comm_key)

    # ── PREDICT live with current values (milliseconds) ──────────────────────
    simulated = {
        "industrial_power_tariff_inr_kwh": power,
        "mn_ore_cif_usd_dmtu": float(mn_ore),
        "imported_coke_cif_usd_mt": float(coke),
        "usd_inr_rate": float(usd_inr),
    }
    pred_result = cost_engine.predict_corridor(cost_artifacts, simulated)

    corr = pred_result["negotiation_corridor"]
    info = cost_artifacts["commodity_info"]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("P10 — Aggressive Offer",
                 f"₹ {corr['p10_aggressive_offer_inr']:,.0f}", "Initial negotiation bid")
    with c2: kpi("P50 — Fair Should-Cost",
                 f"₹ {corr['p50_fair_should_cost_inr']:,.0f}", "AI-derived fair value")
    with c3: kpi("P90 — Upper Ceiling",
                 f"₹ {corr['p90_upper_ceiling_inr']:,.0f}", "Walk-away limit")
    with c4: kpi("Annual Savings Potential",
                 f"₹ {corr['potential_annual_savings_inr']/1e7:.2f} Cr",
                 f"{info['annual_procurement_volume_mt']:,} MT / year")

    col_l, col_r = st.columns([3, 2])

    with col_l:
        section("Historical Actual vs AI Should-Cost")
        hist_df = pd.DataFrame(cost_artifacts["historical_trend"])
        hist_df["date"] = pd.to_datetime(hist_df["date"])

        _fixed = {"date", "industrial_power_tariff_inr_kwh", "mn_ore_cif_usd_dmtu"}
        _data_cols = [c for c in hist_df.columns if c not in _fixed]
        actual_col = next((c for c in _data_cols if "actual" in c or "procured" in c),
                          _data_cols[0])
        _should = [c for c in _data_cols if "should_cost" in c]
        should_col = _should[0] if _should else actual_col

        import plotly.graph_objects as go
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=hist_df["date"], y=hist_df[actual_col],
                                  name="Actual PO Rate",
                                  line=dict(color="#f59e0b", width=2.5)))
        fig2.add_trace(go.Scatter(x=hist_df["date"], y=hist_df[should_col],
                                  name="AI Should-Cost",
                                  line=dict(color="#22d3ee", width=2, dash="dash")))
        fig2.add_hline(y=float(corr["p50_fair_should_cost_inr"]),
                       line_color="#3b82f6", line_width=1.5, line_dash="dot",
                       annotation_text="P50 Sim.", annotation_position="bottom right")
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=10, r=10, t=10, b=10), height=280,
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b", title="Rate (₹/MT)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

        section("P10 / P50 / P90 Negotiation Corridor")
        fig3 = go.Figure(go.Bar(
            x=[corr["p10_aggressive_offer_inr"],
               corr["p50_fair_should_cost_inr"],
               corr["p90_upper_ceiling_inr"]],
            y=["P10 — Aggressive", "P50 — Fair Value", "P90 — Ceiling"],
            orientation="h",
            marker_color=["#22d3ee", "#3b82f6", "#f59e0b"],
            text=[f"₹ {v:,.0f}" for v in [
                corr["p10_aggressive_offer_inr"],
                corr["p50_fair_should_cost_inr"],
                corr["p90_upper_ceiling_inr"]]],
            textposition="outside", textfont=dict(color="#f1f5f9"),
        ))
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            margin=dict(l=10, r=90, t=10, b=10), height=190,
            xaxis=dict(gridcolor="#1e293b", title="Rate (₹/MT)"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_r:
        section("Cost Driver Breakdown")
        driver_df = pd.DataFrame(
            list(info["cost_driver_breakdown"].items()), columns=["Driver", "Share %"])
        import plotly.express as px
        fig4 = px.pie(driver_df, names="Driver", values="Share %", hole=0.5,
                      color_discrete_sequence=["#3b82f6","#22d3ee","#f59e0b","#8b5cf6"])
        fig4.update_traces(textposition="inside", textinfo="percent+label")
        fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                           showlegend=False,
                           margin=dict(l=0, r=0, t=10, b=0), height=240)
        st.plotly_chart(fig4, use_container_width=True)

        section("ML Model Importance Factors")
        imp_df = pd.DataFrame(cost_artifacts["cost_driver_importance"])
        imp_df.columns = ["Market Factor", "AI Importance %"]
        st.dataframe(imp_df, use_container_width=True, hide_index=True)

        section("AutoML Leaderboard")
        lb2 = pd.DataFrame(cost_artifacts["automl_leaderboard"])[
            ["model_id", "rmse", "mape_percent", "r2_score"]]
        lb2.columns = ["Model", "RMSE", "MAPE %", "R²"]
        lb2["Model"] = lb2["Model"].str.replace("H2O_", "").str.replace("_", " ")
        st.dataframe(lb2, use_container_width=True, hide_index=True)

        st.caption(f"Engine: `{cost_artifacts['engine_used']}`")
        st.caption("⚡ Slider changes use live predict — no re-training")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.2rem 0 0.4rem;
     color:#64748b;font-size:0.78rem;border-top:1px solid #1e293b;margin-top:2rem;">
    Steel Authority of India Limited (SAIL) · Bokaro Steel Plant (BSL) · SCM AI Innovation Suite
</div>
""", unsafe_allow_html=True)
