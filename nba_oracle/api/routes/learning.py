from __future__ import annotations

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.health import load_latest_learning_report


router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/status")
def learning_status(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    return load_latest_learning_report()
