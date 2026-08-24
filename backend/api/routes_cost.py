from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from backend.models.cost_prediction import FerroAlloysCostPredictionEngine

router = APIRouter(prefix="/api", tags=["Cost Prediction"])

_engine = None


def _get_engine() -> FerroAlloysCostPredictionEngine:
    global _engine
    if _engine is None:
        _engine = FerroAlloysCostPredictionEngine()
    return _engine


class CostPredictionRequest(BaseModel):
    commodity_key: str = "simn"
    simulated_inputs: Optional[Dict[str, float]] = None


@router.get("/cost/commodities")
def get_commodities():
    """List available ferro alloys and raw material commodities."""
    return _get_engine().get_available_commodities()


@router.post("/cost/predict")
def predict_cost(req: CostPredictionRequest):
    """Run cost prediction with optional What-If simulated market inputs."""
    try:
        return _get_engine().train_and_evaluate(req.commodity_key, req.simulated_inputs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
