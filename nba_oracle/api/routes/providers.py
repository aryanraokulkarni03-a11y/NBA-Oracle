from __future__ import annotations

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.health import load_latest_live_report


router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("/health")
def providers_health(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    report = load_latest_live_report()
    providers = report.get("providers", [])
    return {
        "run_id": report.get("run_id"),
        "providers": providers,
        "degraded_count": sum(1 for row in providers if isinstance(row, dict) and row.get("degraded")),
        "failed_count": sum(1 for row in providers if isinstance(row, dict) and not row.get("success", False)),
    }
