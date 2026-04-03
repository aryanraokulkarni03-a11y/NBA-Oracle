from __future__ import annotations

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.health import load_latest_live_report


router = APIRouter(prefix="/api", tags=["today"])


@router.get("/today")
def today(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    report = load_latest_live_report()
    return {
        "run_id": report.get("run_id"),
        "decision_time": report.get("decision_time"),
        "storage_mode": report.get("storage_mode"),
        "providers": report.get("providers", []),
        "predictions": report.get("predictions", []),
        "stored_paths": report.get("stored_paths", []),
    }
