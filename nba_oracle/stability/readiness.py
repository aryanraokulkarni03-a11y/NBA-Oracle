from __future__ import annotations

from dataclasses import dataclass

from nba_oracle.config import (
    PHASE3_ANALYST_LOGGING_ENABLED,
    PHASE3_MARKET_UNLOCK_MIN_SAMPLE,
    PHASE3_MARKET_UNLOCK_POLICY,
)
from nba_oracle.stability.baseline import LiveRunSnapshot


@dataclass(frozen=True)
class MarketReadiness:
    market: str
    status: str
    active: bool
    reason: str


@dataclass(frozen=True)
class AnalystContainment:
    status: str
    predictor_authority: str
    analyst_logging_enabled: bool
    note: str


@dataclass(frozen=True)
class ReadinessAssessment:
    markets: tuple[MarketReadiness, ...]
    analyst: AnalystContainment
    unlock_policy: str
    graded_predictions: int


def assess_readiness(
    live_runs: tuple[LiveRunSnapshot, ...],
    model_catalog: dict[str, object],
) -> ReadinessAssessment:
    graded_predictions = sum(run.graded_prediction_count for run in live_runs)
    unlock_policy = str(model_catalog.get("market_unlock_policy", PHASE3_MARKET_UNLOCK_POLICY))
    predictor_authority = str(model_catalog.get("predictor_authority", "strict"))
    analyst_present = bool(model_catalog.get("analyst_layer_present", False))
    analyst_logging_enabled = bool(
        model_catalog.get("analyst_logging_enabled", PHASE3_ANALYST_LOGGING_ENABLED)
    )

    markets = (
        MarketReadiness(
            market="moneyline",
            status="active",
            active=True,
            reason="Moneylines stay active as the validated baseline market.",
        ),
        _locked_market("totals", unlock_policy, graded_predictions),
        _locked_market("props", unlock_policy, graded_predictions),
    )

    if predictor_authority == "strict" and analyst_logging_enabled:
        analyst_status = "contained"
        note = (
            "Predictor remains the only decision authority; analyst output is limited to logs and explanation."
        )
    elif predictor_authority == "strict":
        analyst_status = "contained_no_logs"
        note = "Predictor authority is protected, but analyst disagreement logging is still disabled."
    else:
        analyst_status = "risk"
        note = "Predictor authority is not strict; Phase 3 should not treat analyst output as safe."

    if analyst_present:
        note += " Analyst-layer plumbing exists in the catalog."
    else:
        note += " Analyst layer is still absent, which keeps override risk low for now."

    return ReadinessAssessment(
        markets=markets,
        analyst=AnalystContainment(
            status=analyst_status,
            predictor_authority=predictor_authority,
            analyst_logging_enabled=analyst_logging_enabled,
            note=note,
        ),
        unlock_policy=unlock_policy,
        graded_predictions=graded_predictions,
    )


def _locked_market(market: str, unlock_policy: str, graded_predictions: int) -> MarketReadiness:
    if unlock_policy == "strict":
        reason = (
            f"{market.title()} remain locked under strict policy until an explicit promotion event happens."
        )
    elif graded_predictions < PHASE3_MARKET_UNLOCK_MIN_SAMPLE:
        reason = (
            f"{market.title()} remain locked because graded sample is below "
            f"{PHASE3_MARKET_UNLOCK_MIN_SAMPLE}."
        )
    else:
        reason = f"{market.title()} are still locked pending a promotion review."

    return MarketReadiness(
        market=market,
        status="locked",
        active=False,
        reason=reason,
    )
