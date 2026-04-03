from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nba_oracle.config import (
    DEFAULT_STABILITY_JSON_REPORT_PATH,
    DEFAULT_STABILITY_REPORT_PATH,
    REPORTS_DIR,
)
from nba_oracle.models_registry.catalog import ModelRegistryState, model_registry_to_payload
from nba_oracle.stability.baseline import BaselineSnapshot, LiveRunSnapshot, baseline_to_payload
from nba_oracle.stability.drift import DriftAssessment
from nba_oracle.stability.readiness import ReadinessAssessment
from nba_oracle.stability.timing import TimingAssessment


@dataclass(frozen=True)
class StabilityReviewResult:
    review_id: str
    created_at: str
    baseline: BaselineSnapshot
    baseline_action: str
    baseline_reason: str
    live_runs: tuple[LiveRunSnapshot, ...]
    drift: DriftAssessment
    timing: TimingAssessment
    readiness: ReadinessAssessment
    model_catalog: dict[str, object]
    model_registry: ModelRegistryState
    baseline_path: str
    stored_paths: tuple[str, ...]


def write_stability_markdown_report(
    result: StabilityReviewResult,
    path: Path = DEFAULT_STABILITY_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 3 Stability Report")
    lines.append("")
    lines.append(f"- Review id: `{result.review_id}`")
    lines.append(f"- Created at: `{result.created_at}`")
    lines.append(f"- Baseline model version: `{result.baseline.model_version}`")
    lines.append(f"- Baseline action: `{result.baseline_action}`")
    lines.append(f"- Baseline reason: `{result.baseline_reason}`")
    lines.append(f"- Baseline file: `{result.baseline_path}`")
    lines.append(f"- Live runs reviewed: `{len(result.live_runs)}`")
    lines.append(f"- Drift status: `{result.drift.status}`")
    lines.append(f"- Timing status: `{result.timing.status}`")
    lines.append(f"- Analyst containment: `{result.readiness.analyst.status}`")
    lines.append(f"- Model review status: `{result.model_registry.review_status}`")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- Replay ROI: `{result.baseline.replay_roi:.2%}`")
    lines.append(f"- Replay average CLV: `{result.baseline.replay_average_clv:.2%}`")
    lines.append(f"- Replay calibration gap: `{result.baseline.replay_calibration_gap:.4f}`")
    lines.append(f"- Replay average edge: `{result.baseline.replay_average_edge:.2%}`")
    lines.append(f"- Live average active-bet rate: `{result.baseline.live_average_active_bet_rate:.2%}`")
    lines.append(f"- Live average skip rate: `{result.baseline.live_average_skip_rate:.2%}`")
    lines.append(f"- Live average source quality: `{result.baseline.live_average_source_quality:.2%}`")
    lines.append(f"- Config fingerprint: `{result.baseline.config_fingerprint}`")
    lines.append("")
    lines.append("## Drift Signals")
    lines.append("")
    lines.append("| Signal | Available | Sample | Baseline | Current | Delta | Threshold | Triggered |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|")
    for signal in result.drift.signals:
        current = f"{signal.current_value:.4f}" if signal.available else "n/a"
        delta = f"{signal.delta:.4f}" if signal.available else "n/a"
        lines.append(
            f"| {signal.name} | {signal.available} | {signal.sample_size} | {signal.baseline_value:.4f} | "
            f"{current} | {delta} | {signal.threshold:.4f} | {signal.triggered} |"
        )
    lines.append("")
    lines.append("### Outcome Metrics")
    lines.append("")
    lines.append(f"- Graded BET count: `{result.drift.outcome_metrics.graded_bet_count}`")
    lines.append(f"- Graded actionable count: `{result.drift.outcome_metrics.graded_actionable_count}`")
    lines.append(f"- Live ROI: `{_fmt_optional_percent(result.drift.outcome_metrics.roi)}`")
    lines.append(f"- Live CLV: `{_fmt_optional_percent(result.drift.outcome_metrics.average_clv)}`")
    lines.append(f"- Live calibration gap: `{_fmt_optional_float(result.drift.outcome_metrics.calibration_gap)}`")
    for reason in result.drift.reasons:
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Timing")
    lines.append("")
    lines.append(f"- Average source age (minutes): `{result.timing.average_source_age_minutes:.2f}`")
    lines.append(f"- Average market age (minutes): `{result.timing.average_market_age_minutes:.2f}`")
    lines.append(f"- Stale source count: `{result.timing.stale_source_count}`")
    lines.append(f"- Schedule fallback rate: `{result.timing.schedule_fallback_rate:.2%}`")
    lines.append(f"- Timing event count: `{len(result.timing.events)}`")
    for note in result.timing.notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Market Readiness")
    lines.append("")
    lines.append("| Market | Status | Active | Graded sample | Calibration gap | CLV | Skip rate | Missing requirements |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|")
    for market in result.readiness.markets:
        lines.append(
            f"| {market.market} | {market.status} | {market.active} | {market.evidence.graded_sample_count} | "
            f"{_fmt_optional_float(market.evidence.calibration_gap)} | {_fmt_optional_percent(market.evidence.average_clv)} | "
            f"{market.evidence.skip_rate:.2%} | {', '.join(market.evidence.missing_requirements) or 'none'} |"
        )
    lines.append("")
    lines.append("## Analyst Containment")
    lines.append("")
    lines.append(f"- Predictor authority: `{result.readiness.analyst.predictor_authority}`")
    lines.append(f"- Analyst logging enabled: `{result.readiness.analyst.analyst_logging_enabled}`")
    lines.append(f"- Disagreement count: `{result.readiness.analyst.disagreement_count}`")
    lines.append(f"- Note: {result.readiness.analyst.note}")
    lines.append("")
    lines.append("## Recent Live Runs")
    lines.append("")
    lines.append("| Run id | Predictions | BET rate | Skip rate | Avg quality | Avg edge | Avg CLV | Provider degradation |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for run in result.live_runs:
        lines.append(
            f"| {run.run_id} | {run.prediction_count} | {run.active_bet_rate:.2%} | {run.skip_rate:.2%} | "
            f"{run.average_source_quality:.2%} | {run.average_edge:.2%} | {run.average_clv:.2%} | {run.provider_degradation_rate:.2%} |"
        )
    lines.append("")
    lines.append("## Stored Artifacts")
    lines.append("")
    for stored_path in result.stored_paths:
        lines.append(f"- `{stored_path}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_stability_json_report(
    result: StabilityReviewResult,
    path: Path = DEFAULT_STABILITY_JSON_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "review_id": result.review_id,
        "created_at": result.created_at,
        "baseline_action": result.baseline_action,
        "baseline_reason": result.baseline_reason,
        "baseline": baseline_to_payload(result.baseline),
        "baseline_path": result.baseline_path,
        "drift": {
            "status": result.drift.status,
            "live_runs_considered": result.drift.live_runs_considered,
            "graded_predictions": result.drift.graded_predictions,
            "retraining_recommended": result.drift.retraining_recommended,
            "reasons": list(result.drift.reasons),
            "outcome_metrics": {
                "graded_bet_count": result.drift.outcome_metrics.graded_bet_count,
                "graded_actionable_count": result.drift.outcome_metrics.graded_actionable_count,
                "roi": result.drift.outcome_metrics.roi,
                "average_clv": result.drift.outcome_metrics.average_clv,
                "calibration_gap": result.drift.outcome_metrics.calibration_gap,
            },
            "signals": [
                {
                    "name": signal.name,
                    "baseline_value": signal.baseline_value,
                    "current_value": signal.current_value,
                    "delta": signal.delta,
                    "threshold": signal.threshold,
                    "triggered": signal.triggered,
                    "available": signal.available,
                    "sample_size": signal.sample_size,
                    "note": signal.note,
                }
                for signal in result.drift.signals
            ],
        },
        "timing": {
            "status": result.timing.status,
            "runs_considered": result.timing.runs_considered,
            "stale_source_count": result.timing.stale_source_count,
            "average_source_age_minutes": result.timing.average_source_age_minutes,
            "average_market_age_minutes": result.timing.average_market_age_minutes,
            "schedule_fallback_rate": result.timing.schedule_fallback_rate,
            "notes": list(result.timing.notes),
            "events": [
                {
                    "review_id": event.review_id,
                    "run_id": event.run_id,
                    "game_id": event.game_id,
                    "event_type": event.event_type,
                    "source_kind": event.source_kind,
                    "source_name": event.source_name,
                    "source_timestamp": event.source_timestamp,
                    "decision_timestamp": event.decision_timestamp,
                    "market_timestamp": event.market_timestamp,
                    "market_already_moved": event.market_already_moved,
                    "predictor_changed": event.predictor_changed,
                    "decision": event.decision,
                    "event_impact": event.event_impact,
                    "age_minutes": event.age_minutes,
                    "signal_delta": event.signal_delta,
                }
                for event in result.timing.events
            ],
        },
        "readiness": {
            "unlock_policy": result.readiness.unlock_policy,
            "graded_predictions": result.readiness.graded_predictions,
            "markets": [
                {
                    "market": market.market,
                    "status": market.status,
                    "active": market.active,
                    "reason": market.reason,
                    "evidence": {
                        "graded_sample_count": market.evidence.graded_sample_count,
                        "calibration_gap": market.evidence.calibration_gap,
                        "average_clv": market.evidence.average_clv,
                        "skip_rate": market.evidence.skip_rate,
                        "operator_review_required": market.evidence.operator_review_required,
                        "missing_requirements": list(market.evidence.missing_requirements),
                    },
                }
                for market in result.readiness.markets
            ],
            "analyst": {
                "status": result.readiness.analyst.status,
                "predictor_authority": result.readiness.analyst.predictor_authority,
                "analyst_logging_enabled": result.readiness.analyst.analyst_logging_enabled,
                "disagreement_count": result.readiness.analyst.disagreement_count,
                "note": result.readiness.analyst.note,
                "logs": [
                    {
                        "review_id": log.review_id,
                        "game_id": log.game_id,
                        "disagreement_type": log.disagreement_type,
                        "predictor_decision": log.predictor_decision,
                        "analyst_decision": log.analyst_decision,
                        "final_authority": log.final_authority,
                        "note": log.note,
                    }
                    for log in result.readiness.analyst_logs
                ],
            },
        },
        "model_catalog": result.model_catalog,
        "model_registry": model_registry_to_payload(result.model_registry),
        "live_runs": [
            {
                "run_id": run.run_id,
                "decision_time": run.decision_time.isoformat(),
                "prediction_count": run.prediction_count,
                "active_bet_rate": run.active_bet_rate,
                "skip_rate": run.skip_rate,
                "average_source_quality": run.average_source_quality,
                "average_expected_value": run.average_expected_value,
                "average_edge": run.average_edge,
                "average_clv": run.average_clv,
                "provider_degradation_rate": run.provider_degradation_rate,
                "schedule_fallback_used": run.schedule_fallback_used,
            }
            for run in result.live_runs
        ],
        "stored_paths": list(result.stored_paths),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _fmt_optional_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2%}"


def _fmt_optional_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}"
