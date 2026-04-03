from __future__ import annotations

from dataclasses import dataclass

from nba_oracle.config import (
    PHASE3_ANALYST_LOGGING_ENABLED,
    PHASE3_MARKET_UNLOCK_MIN_SAMPLE,
    PHASE3_MARKET_UNLOCK_POLICY,
)
from nba_oracle.stability.baseline import BaselineSnapshot, LiveRunSnapshot
from nba_oracle.stability.drift import DriftAssessment


@dataclass(frozen=True)
class MarketEvidence:
    graded_sample_count: int
    calibration_gap: float | None
    average_clv: float | None
    skip_rate: float
    operator_review_required: bool
    missing_requirements: tuple[str, ...]


@dataclass(frozen=True)
class MarketReadiness:
    market: str
    status: str
    active: bool
    reason: str
    evidence: MarketEvidence


@dataclass(frozen=True)
class AnalystContainment:
    status: str
    predictor_authority: str
    analyst_logging_enabled: bool
    disagreement_count: int
    note: str


@dataclass(frozen=True)
class AnalystDisagreementLog:
    review_id: str
    game_id: str
    disagreement_type: str
    predictor_decision: str
    analyst_decision: str | None
    final_authority: str
    note: str


@dataclass(frozen=True)
class ReadinessAssessment:
    markets: tuple[MarketReadiness, ...]
    analyst: AnalystContainment
    unlock_policy: str
    graded_predictions: int
    analyst_logs: tuple[AnalystDisagreementLog, ...]


def assess_readiness(
    review_id: str,
    live_runs: tuple[LiveRunSnapshot, ...],
    model_catalog: dict[str, object],
    baseline: BaselineSnapshot,
    drift: DriftAssessment,
    analyst_payload: dict[str, dict[str, object]] | None = None,
) -> ReadinessAssessment:
    graded_predictions = sum(run.graded_prediction_count for run in live_runs)
    unlock_policy = str(model_catalog.get("market_unlock_policy", PHASE3_MARKET_UNLOCK_POLICY))
    predictor_authority = str(model_catalog.get("predictor_authority", "strict"))
    analyst_present = bool(model_catalog.get("analyst_layer_present", False))
    analyst_logging_enabled = bool(
        model_catalog.get("analyst_logging_enabled", PHASE3_ANALYST_LOGGING_ENABLED)
    )

    moneyline_evidence = _build_moneyline_evidence(live_runs, baseline, drift)
    markets = (
        MarketReadiness(
            market="moneyline",
            status="active",
            active=True,
            reason="Moneylines stay active as the validated baseline market.",
            evidence=moneyline_evidence,
        ),
        _locked_market("totals", unlock_policy, moneyline_evidence),
        _locked_market("props", unlock_policy, moneyline_evidence),
    )

    analyst_logs = build_analyst_logs(review_id, live_runs, analyst_payload)
    disagreement_count = len(analyst_logs)

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
            disagreement_count=disagreement_count,
            note=note,
        ),
        unlock_policy=unlock_policy,
        graded_predictions=graded_predictions,
        analyst_logs=analyst_logs,
    )


def build_analyst_logs(
    review_id: str,
    live_runs: tuple[LiveRunSnapshot, ...],
    analyst_payload: dict[str, dict[str, object]] | None,
) -> tuple[AnalystDisagreementLog, ...]:
    if not analyst_payload:
        return ()

    logs: list[AnalystDisagreementLog] = []
    for run in live_runs:
        for prediction in run.predictions:
            suggestion = analyst_payload.get(prediction.game_id)
            if suggestion is None:
                continue
            analyst_decision = str(suggestion.get("decision", "")).upper() or None
            if analyst_decision == prediction.decision:
                continue
            logs.append(
                AnalystDisagreementLog(
                    review_id=review_id,
                    game_id=prediction.game_id,
                    disagreement_type=_classify_disagreement(prediction.decision, analyst_decision),
                    predictor_decision=prediction.decision,
                    analyst_decision=analyst_decision,
                    final_authority="predictor",
                    note="Predictor output remains authoritative over analyst suggestion.",
                )
            )
    return tuple(logs)


def _build_moneyline_evidence(
    live_runs: tuple[LiveRunSnapshot, ...],
    baseline: BaselineSnapshot,
    drift: DriftAssessment,
) -> MarketEvidence:
    active_runs = tuple(run for run in live_runs if run.prediction_count > 0)
    skip_rate = round(sum(run.skip_rate for run in active_runs) / len(active_runs), 4) if active_runs else 0.0
    calibration_gap = drift.outcome_metrics.calibration_gap
    average_clv = drift.outcome_metrics.average_clv

    missing_requirements: list[str] = []
    if drift.outcome_metrics.graded_actionable_count < PHASE3_MARKET_UNLOCK_MIN_SAMPLE:
        missing_requirements.append("graded_sample_below_unlock_threshold")
    if calibration_gap is None:
        missing_requirements.append("calibration_gap_unavailable")
    if average_clv is None:
        missing_requirements.append("clv_unavailable")
    if skip_rate > max(baseline.live_average_skip_rate + 0.2, 0.9):
        missing_requirements.append("skip_rate_out_of_bounds")

    return MarketEvidence(
        graded_sample_count=drift.outcome_metrics.graded_actionable_count,
        calibration_gap=calibration_gap,
        average_clv=average_clv,
        skip_rate=skip_rate,
        operator_review_required=True,
        missing_requirements=tuple(missing_requirements),
    )


def _locked_market(market: str, unlock_policy: str, moneyline_evidence: MarketEvidence) -> MarketReadiness:
    missing_requirements = list(moneyline_evidence.missing_requirements)
    if unlock_policy == "strict":
        missing_requirements.insert(0, "strict_policy_requires_explicit_promotion")
        reason = (
            f"{market.title()} remain locked under strict policy until an explicit promotion event happens."
        )
    else:
        reason = (
            f"{market.title()} remain locked because unlock evidence is incomplete."
            if missing_requirements
            else f"{market.title()} remain locked pending manual promotion review."
        )

    return MarketReadiness(
        market=market,
        status="locked",
        active=False,
        reason=reason,
        evidence=MarketEvidence(
            graded_sample_count=moneyline_evidence.graded_sample_count,
            calibration_gap=moneyline_evidence.calibration_gap,
            average_clv=moneyline_evidence.average_clv,
            skip_rate=moneyline_evidence.skip_rate,
            operator_review_required=True,
            missing_requirements=tuple(missing_requirements),
        ),
    )


def _classify_disagreement(predictor_decision: str, analyst_decision: str | None) -> str:
    if analyst_decision is None:
        return "missing_analyst_decision"
    if predictor_decision == "SKIP" and analyst_decision != "SKIP":
        return "analyst_wants_activation"
    if predictor_decision != "SKIP" and analyst_decision == "SKIP":
        return "analyst_wants_cancellation"
    return "decision_mismatch"
