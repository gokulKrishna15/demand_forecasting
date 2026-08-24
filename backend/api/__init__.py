"""API routers package init (placeholders for Phase 2-4)."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}