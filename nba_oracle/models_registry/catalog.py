from __future__ import annotations

from nba_oracle.config import PHASE3_ANALYST_LOGGING_ENABLED, PHASE3_MARKET_UNLOCK_POLICY


def build_model_catalog() -> dict[str, object]:
    return {
        "model_version": "phase2-deterministic-v1",
        "active_market_family": "moneyline",
        "market_unlock_policy": PHASE3_MARKET_UNLOCK_POLICY,
        "analyst_layer_present": False,
        "analyst_logging_enabled": PHASE3_ANALYST_LOGGING_ENABLED,
        "retraining_policy": "manual_review_only",
        "predictor_authority": "strict",
    }
