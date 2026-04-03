from __future__ import annotations

from fastapi import APIRouter

from nba_oracle.config import ORACLE_PASSWORD_HASH
from nba_oracle.runtime.health import build_health_snapshot


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    snapshot = build_health_snapshot()
    snapshot["auth"] = {"bootstrapped": bool(ORACLE_PASSWORD_HASH)}
    return snapshot
