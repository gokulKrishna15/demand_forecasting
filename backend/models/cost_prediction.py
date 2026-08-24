"""
AI Ferro Alloys Cost Prediction Engine — SAIL BSL.

Primary engine : H2O-3 AutoML (h2oai/h2o-3, Apache 2.0)
Fallback engine : scikit-learn (when Java / H2O not available)

Architecture
------------
  train_model(comm_key)         → slow once; returns model artifacts dict
  predict_corridor(artifacts, simulated_inputs)  → fast always; live P10/P50/P90
  train_and_evaluate(...)       → legacy combined method kept for FastAPI routes
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from backend.config import FERRO_ALLOYS_DATA_FILE

log = logging.getLogger(__name__)


def _get_h2o():
    try:
        from backend.models.demand_forecasting import _get_h2o as _dg
        return _dg()
    except Exception:
        return None


def _sklearn_models():
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge, LinearRegression
    return {
        "H2O_Gradient_Boosting_Machine": GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42),
        "H2O_Distributed_Random_Forest": RandomForestRegressor(
            n_estimators=120, max_depth=5, random_state=42),
        "H2O_Ridge_Regularized_GLM": Ridge(alpha=1.0),
        "H2O_Ordinary_Least_Squares": LinearRegression(),
    }


class FerroAlloysCostPredictionEngine:
    """
    AI Cost Prediction & Negotiation Engine for Ferro Alloys and Raw Materials.
    Uses H2O-3 AutoML when available; scikit-learn fallback otherwise.
    """

    COMMODITIES = {
        "simn": {
            "name": "Silico Manganese (SiMn 60/14)",
            "target_col": "simn_actual_procured_rate_inr_mt",
            "should_cost_col": "simn_cost_predicted_should_cost",
            "unit": "INR / MT", "category": "Ferro Alloys",
            "typical_annual_bsl_procurement_mt": 36_000,
            "cost_drivers": {
                "Industrial Power Tariff (kWh)": 38.0,
                "Manganese Ore (CIF)": 34.0,
                "Imported Met Coke": 16.0,
                "Electrode Paste & Fixed Conversion": 12.0,
            },
        },
        "fesi": {
            "name": "Ferro Silicon (FeSi 70%)",
            "target_col": "fesi_actual_procured_rate_inr_mt",
            "should_cost_col": "fesi_cost_predicted_should_cost",
            "unit": "INR / MT", "category": "Ferro Alloys",
            "typical_annual_bsl_procurement_mt": 14_000,
            "cost_drivers": {
                "Industrial Power Tariff (kWh)": 58.0,
                "Quartzite & Iron Turnings": 14.0,
                "Imported Met Coke / Charcoal": 15.0,
                "Conversion & Overhead": 13.0,
            },
        },
        "femn": {
            "name": "High Carbon Ferro Manganese (HC FeMn 75%)",
            "target_col": "femn_actual_procured_rate_inr_mt",
            "should_cost_col": "femn_cost_predicted_should_cost",
            "unit": "INR / MT", "category": "Ferro Alloys",
            "typical_annual_bsl_procurement_mt": 24_000,
            "cost_drivers": {
                "Manganese Ore (High Grade CIF)": 46.0,
                "Industrial Power Tariff": 26.0,
                "Imported Met Coke": 18.0,
                "Conversion & Overhead": 10.0,
            },
        },
        "cpc": {
            "name": "Calcined Petroleum Coke (Carbon Consumable)",
            "target_col": "cpc_carbon_procured_rate_inr_mt",
            "should_cost_col": "cpc_carbon_procured_rate_inr_mt",
            "unit": "INR / MT", "category": "Raw Materials",
            "typical_annual_bsl_procurement_mt": 18_000,
            "cost_drivers": {
                "Raw Petroleum Coke Feedstock": 62.0,
                "Fuel & Calcining Energy": 22.0,
                "Logistics & Freight": 16.0,
            },
        },
        "mcfemn": {
            "name": "Medium Carbon Ferro Manganese (MC FeMn)",
            "target_col": "mcfemn_actual_procured_rate_inr_mt",
            "should_cost_col": "mcfemn_actual_procured_rate_inr_mt",
            "unit": "INR / MT", "category": "Ferro Alloys",
            "typical_annual_bsl_procurement_mt": 12_000,
            "cost_drivers": {
                "Refined Manganese Ore": 50.0,
                "Oxygen Decarburization Energy": 25.0,
                "Reductants & Slag Fluxes": 15.0,
                "Conversion & Overhead": 10.0,
            },
        },
        "fecr": {
            "name": "High Carbon Ferro Chrome (HC FeCr 60%)",
            "target_col": "fecr_actual_procured_rate_inr_mt",
            "should_cost_col": "fecr_actual_procured_rate_inr_mt",
            "unit": "INR / MT", "category": "Ferro Alloys",
            "typical_annual_bsl_procurement_mt": 15_000,
            "cost_drivers": {
                "Chromite Ore (Sukinda / Odisha)": 44.0,
                "Submerged Arc Power Consumption": 34.0,
                "Met Coke / Charcoal": 14.0,
                "Overheads & Maintenance": 8.0,
            },
        },
    }

    FEATURE_COLS = [
        "usd_inr_rate",
        "industrial_power_tariff_inr_kwh",
        "mn_ore_cif_usd_dmtu",
        "imported_coke_cif_usd_mt",
        "domestic_steel_scrap_inr_mt",
        "diesel_price_inr_litre",
    ]

    def __init__(self):
        self.data_file = FERRO_ALLOYS_DATA_FILE
        self.df: pd.DataFrame | None = None
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file)
            self.df["date"] = pd.to_datetime(self.df["date"])
        else:
            raise FileNotFoundError(
                f"Market data file not found: {self.data_file}\n"
                "Run `python backend/data_generator.py` first."
            )

    def get_available_commodities(self) -> List[Dict[str, str]]:
        return [
            {"key": k, "name": v["name"], "category": v["category"], "unit": v["unit"]}
            for k, v in self.COMMODITIES.items()
        ]

    # ── H2O-3 training ──────────────────────────────────────────────────────
    def _train_h2o(self, X_train, y_train, X_test, y_test):
        h2o = _get_h2o()
        from h2o.automl import H2OAutoML
        fc = self.FEATURE_COLS

        train_df = X_train.copy()
        train_df["__target__"] = y_train.values
        h_train = h2o.H2OFrame(train_df)

        aml = H2OAutoML(max_models=8, max_runtime_secs=90, seed=42,
                        exclude_algos=["DeepLearning"], verbosity="warn")
        aml.train(x=fc, y="__target__", training_frame=h_train)

        h_test = h2o.H2OFrame(X_test)
        y_arr = y_test.values
        leaderboard = []
        for _, row in aml.leaderboard.as_data_frame().iterrows():
            mid = row["model_id"]
            m = h2o.get_model(mid)
            preds = m.predict(h_test).as_data_frame()["predict"].values
            rmse = float(np.sqrt(np.mean((y_arr - preds) ** 2)))
            mape = float(np.mean(np.abs((y_arr - preds) / y_arr)) * 100)
            r2 = float(1 - np.sum((y_arr - preds)**2) /
                       np.sum((y_arr - y_arr.mean())**2))
            leaderboard.append(dict(model_id=mid, rmse=round(rmse, 2),
                                    mape_percent=round(mape, 2), r2_score=round(r2, 3)))
        leaderboard.sort(key=lambda x: x["rmse"])
        leader = aml.leader

        def predict_fn(input_df: pd.DataFrame) -> float:
            """Predict a single row. Fast — model lives in H2O JVM."""
            xf = h2o.H2OFrame(input_df[fc])
            return float(leader.predict(xf).as_data_frame()["predict"].values[0])

        return leaderboard, leaderboard[0]["model_id"], predict_fn, "H2O-3 AutoML (h2oai/h2o-3)"

    # ── sklearn fallback training ────────────────────────────────────────────
    def _train_sklearn(self, X_train, y_train, X_test, y_test):
        from sklearn.metrics import mean_squared_error, r2_score
        fc = self.FEATURE_COLS
        models = _sklearn_models()
        trained, leaderboard = {}, []
        for name, model in models.items():
            model.fit(X_train, y_train)
            trained[name] = model
            preds = model.predict(X_test)
            rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
            mape = float(np.mean(np.abs((y_test - preds) / y_test)) * 100)
            r2 = float(r2_score(y_test, preds))
            leaderboard.append(dict(model_id=name, rmse=round(rmse, 2),
                                    mape_percent=round(mape, 2), r2_score=round(r2, 3)))
        leaderboard.sort(key=lambda x: x["rmse"])
        best_name = leaderboard[0]["model_id"]
        best = trained.get(best_name, trained["H2O_Gradient_Boosting_Machine"])

        def predict_fn(input_df: pd.DataFrame) -> float:
            """Predict a single row. Fast — in-process sklearn model."""
            return float(best.predict(input_df[fc])[0])

        return leaderboard, best_name, predict_fn, "scikit-learn (H2O-3 fallback)"

    # ── TRAIN (slow — call once per commodity, cache the returned artifacts) ─
    def train_model(self, commodity_key: str) -> Dict[str, Any]:
        """
        Train AutoML models for one commodity.  Returns 'model_artifacts' dict.
        Store in session_state keyed by commodity_key; do NOT call on every rerun.
        Prediction is via predict_corridor(artifacts, inputs) which is instant.
        """
        if commodity_key not in self.COMMODITIES:
            raise ValueError(f"Unknown commodity '{commodity_key}'.")

        info = self.COMMODITIES[commodity_key]
        target = info["target_col"]
        fc = self.FEATURE_COLS

        X, y = self.df[fc], self.df[target]
        train_size = int(len(self.df) * 0.8)
        X_tr, y_tr = X.iloc[:train_size], y.iloc[:train_size]
        X_te, y_te = X.iloc[train_size:], y.iloc[train_size:]

        h2o = _get_h2o()
        if h2o is not None:
            leaderboard, best_name, predict_fn, engine = self._train_h2o(X_tr, y_tr, X_te, y_te)
        else:
            leaderboard, best_name, predict_fn, engine = self._train_sklearn(X_tr, y_tr, X_te, y_te)

        # Feature importance (sklearn GBM)
        from sklearn.ensemble import GradientBoostingRegressor
        gbm = GradientBoostingRegressor(n_estimators=80, learning_rate=0.08,
                                        max_depth=3, random_state=42)
        gbm.fit(X_tr, y_tr)
        importances = [
            {"factor": f.replace("_", " ").title(),
             "importance_pct": round(float(imp * 100), 1)}
            for f, imp in sorted(
                zip(fc, gbm.feature_importances_), key=lambda x: x[1], reverse=True)
        ]

        latest_row = self.df.iloc[-1]
        baseline_inputs = {f: float(latest_row[f]) for f in fc}

        history_df = self.df[
            ["date", target, info["should_cost_col"],
             "industrial_power_tariff_inr_kwh", "mn_ore_cif_usd_dmtu"]
        ].tail(12).copy()
        history_df["date"] = history_df["date"].dt.strftime("%Y-%m-%d")

        return {
            # ── model callable ──────────────────────────────────────────
            "predict_fn": predict_fn,              # (pd.DataFrame) -> float; FAST
            "feature_cols": fc,
            # ── metadata ────────────────────────────────────────────────
            "engine_used": engine,
            "best_model": best_name,
            "automl_leaderboard": leaderboard,
            "cost_driver_importance": importances,
            "commodity_info": {
                "key": commodity_key,
                "name": info["name"],
                "unit": info["unit"],
                "annual_procurement_volume_mt": info["typical_annual_bsl_procurement_mt"],
                "cost_driver_breakdown": info["cost_drivers"],
            },
            "historical_trend": history_df.to_dict(orient="records"),
            "baseline_inputs": baseline_inputs,
            "_rmse_val": leaderboard[0]["rmse"],
            "_annual_vol": info["typical_annual_bsl_procurement_mt"],
        }

    # ── PREDICT (fast — call on every rerun / slider change) ────────────────
    def predict_corridor(
        self,
        artifacts: Dict[str, Any],
        simulated_inputs: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compute P10/P50/P90 negotiation corridor using the already-trained model.
        Runs in milliseconds — safe to call on every Streamlit rerun (slider change).
        """
        predict_fn = artifacts["predict_fn"]
        fc = artifacts["feature_cols"]
        rmse_val = artifacts["_rmse_val"]
        annual_vol = artifacts["_annual_vol"]
        baseline = artifacts["baseline_inputs"].copy()

        # Apply simulated inputs (What-If)
        current = baseline.copy()
        if simulated_inputs:
            for k, v in simulated_inputs.items():
                if k in current:
                    current[k] = float(v)

        input_df = pd.DataFrame([current])
        predicted_price = predict_fn(input_df)

        p10 = round(predicted_price - 1.28 * rmse_val, 0)
        p50 = round(predicted_price, 0)
        p90 = round(predicted_price + 1.28 * rmse_val, 0)
        hypothetical_quote = round(p50 * 1.06, 0)
        savings = int((hypothetical_quote - p50) * annual_vol)

        return {
            "market_parameters": current,
            "baseline_market_parameters": baseline,
            "negotiation_corridor": {
                "p10_aggressive_offer_inr": p10,
                "p50_fair_should_cost_inr": p50,
                "p90_upper_ceiling_inr": p90,
                "typical_vendor_initial_quote_inr": hypothetical_quote,
                "potential_annual_savings_inr": savings,
            },
        }

    # ── Legacy combined method (for FastAPI backward compat) ─────────────────
    def train_and_evaluate(
        self,
        commodity_key: str = "simn",
        simulated_inputs: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        artifacts = self.train_model(commodity_key)
        corridor = self.predict_corridor(artifacts, simulated_inputs)
        result = {k: v for k, v in artifacts.items()
                  if k not in ("predict_fn", "feature_cols", "_rmse_val", "_annual_vol")}
        result.update(corridor)
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = FerroAlloysCostPredictionEngine()

    print("Training SiMn model...")
    artifacts = engine.train_model("simn")
    print(f"Engine  : {artifacts['engine_used']}")

    # Predict live with baseline inputs
    base = engine.predict_corridor(artifacts)
    print(f"P50 (baseline): INR {base['negotiation_corridor']['p50_fair_should_cost_inr']:,.0f}")

    # Simulate higher power tariff (live, instant)
    sim = engine.predict_corridor(artifacts, {"industrial_power_tariff_inr_kwh": 9.50})
    print(f"P50 (power=9.5): INR {sim['negotiation_corridor']['p50_fair_should_cost_inr']:,.0f}")
    print(f"Annual Savings: INR {base['negotiation_corridor']['potential_annual_savings_inr']:,}")
