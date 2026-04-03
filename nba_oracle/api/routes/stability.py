from __future__ import annotations

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.health import load_latest_stability_report


router = APIRouter(prefix="/api/stability", tags=["stability"])


@router.get("/latest")
def latest_stability(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    return load_latest_stability_report()
