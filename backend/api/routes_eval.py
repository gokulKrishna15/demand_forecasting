from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.tender_evaluation import TenderEvaluationEngine

router = APIRouter(prefix="/api", tags=["Tender Evaluation"])

_engine = None


def _get_engine() -> TenderEvaluationEngine:
    global _engine
    if _engine is None:
        _engine = TenderEvaluationEngine()
    return _engine


class EvalQuery(BaseModel):
    query: Optional[str] = ""

    class Config:
        extra = "allow"


@router.get("/tender/evaluate")
def run_evaluation():
    """Full tender CST evaluation with vendor scoring and recommendation."""
    try:
        return _get_engine().evaluate_tender()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/tender/recommendation")
def get_recommendation():
    """Quick executive purchase recommendation (L1 bidder + justification)."""
    try:
        res = _get_engine().evaluate_tender()
        return res["executive_purchase_recommendation"]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
