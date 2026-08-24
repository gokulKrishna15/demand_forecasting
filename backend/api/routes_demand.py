from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from backend.models.demand_forecasting import DemandForecastingEngine

router = APIRouter(prefix="/api", tags=["Demand Forecasting"])

_engine = None


def _get_engine() -> DemandForecastingEngine:
    global _engine
    if _engine is None:
        _engine = DemandForecastingEngine()
    return _engine


class DemandForecastRequest(BaseModel):
    item_id: str
    horizon_months: int = 6


@router.get("/demand/items")
def get_items():
    """List all monitored spare parts / consumables."""
    return _get_engine().get_items_list()


@router.post("/demand/forecast")
def run_forecast(req: DemandForecastRequest):
    """Run AutoML demand forecast for a given item."""
    try:
        return _get_engine().train_and_forecast(req.item_id, req.horizon_months)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
