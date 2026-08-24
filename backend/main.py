"""
SAIL BSL SCM AI Innovation Suite — FastAPI Backend
===================================================
Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import routes_cost, routes_demand, routes_eval

app = FastAPI(
    title="SAIL Bokaro Steel Plant — SCM AI Innovation Suite",
    description=(
        "REST API for the three AI initiatives from the Bokaro Niwas workshop: "
        "Demand Forecasting, Tender Evaluation, and Ferro Alloys Cost Prediction. "
        "100% Free & Open-Source (H2O-3, Apache 2.0)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_demand.router)
app.include_router(routes_cost.router)
app.include_router(routes_eval.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "plant": "Steel Authority of India Limited (SAIL) — Bokaro Steel Plant (BSL)",
        "modules": [
            "AI Demand Forecasting",
            "AI Tender Bid Evaluation",
            "AI Ferro Alloys Cost Prediction",
        ],
        "backend": "H2O-3 AutoML (h2oai/h2o-3) + scikit-learn fallback",
        "frontend": "Streamlit (open-source, Apache 2.0)",
        "license": "100% Free & Open-Source (Apache 2.0 / MIT)",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)