from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nba_oracle.config import (
    DEFAULT_STABILITY_JSON_REPORT_PATH,
    DEFAULT_STABILITY_REPORT_PATH,
    REPORTS_DIR,
)
from nba_oracle.stability.baseline import BaselineSnapshot, LiveRunSnapshot
from nba_oracle.stability.drift import DriftAssessment
from nba_oracle.stability.readiness import ReadinessAssessment
from nba_oracle.stability.timing import TimingAssessment


@dataclass(frozen=True)
class StabilityReviewResult:
    baseline: BaselineSnapshot
    live_runs: tuple[LiveRunSnapshot, ...]
    drift: DriftAssessment
    timing: TimingAssessment
    readiness: ReadinessAssessment
    model_catalog: dict[str, object]
    baseline_path: str


def write_stability_markdown_report(
    result: StabilityReviewResult,
    path: Path = DEFAULT_STABILITY_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 3 Stability Report")
    lines.append("")
    lines.append(f"- Baseline model version: `{result.baseline.model_version}`")
    lines.append(f"- Baseline file: `{result.baseline_path}`")
    lines.append(f"- Live runs reviewed: `{len(result.live_runs)}`")
    lines.append(f"- Drift status: `{result.drift.status}`")
    lines.append(f"- Timing status: `{result.timing.status}`")
    lines.append(f"- Analyst containment: `{result.readiness.analyst.status}`")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- Replay ROI: `{result.baseline.replay_roi:.2%}`")
    lines.append(f"- Replay average CLV: `{result.baseline.replay_average_clv:.2%}`")
    lines.append(f"- Replay average edge: `{result.baseline.replay_average_edge:.2%}`")
    lines.append(f"- Replay average source quality: `{result.baseline.replay_average_source_quality:.2%}`")
    lines.append(f"- Live average active-bet rate: `{result.baseline.live_average_active_bet_rate:.2%}`")
    lines.append(f"- Live average skip rate: `{result.baseline.live_average_skip_rate:.2%}`")
    lines.append(f"- Live average source quality: `{result.baseline.live_average_source_quality:.2%}`")
    lines.append("")
    lines.append("## Drift Signals")
    lines.append("")
    lines.append("| Signal | Baseline | Current | Delta | Threshold | Triggered |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for signal in result.drift.signals:
        lines.append(
            f"| {signal.name} | {signal.baseline_value:.4f} | {signal.current_value:.4f} | "
            f"{signal.delta:.4f} | {signal.threshold:.4f} | {signal.triggered} |"
        )
    lines.append("")
    for reason in result.drift.reasons:
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Timing")
    lines.append("")
    lines.append(f"- Average source age (minutes): `{result.timing.average_source_age_minutes:.2f}`")
    lines.append(f"- Average market age (minutes): `{result.timing.average_market_age_minutes:.2f}`")
    lines.append(f"- Stale source count: `{result.timing.stale_source_count}`")
    lines.append(f"- Schedule fallback rate: `{result.timing.schedule_fallback_rate:.2%}`")
    for note in result.timing.notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Market Readiness")
    lines.append("")
    lines.append("| Market | Status | Active | Reason |")
    lines.append("|---|---|---|---|")
    for market in result.readiness.markets:
        lines.append(f"| {market.market} | {market.status} | {market.active} | {market.reason} |")
    lines.append("")
    lines.append("## Analyst Containment")
    lines.append("")
    lines.append(f"- Predictor authority: `{result.readiness.analyst.predictor_authority}`")
    lines.append(f"- Analyst logging enabled: `{result.readiness.analyst.analyst_logging_enabled}`")
    lines.append(f"- Note: {result.readiness.analyst.note}")
    lines.append("")
    lines.append("## Recent Live Runs")
    lines.append("")
    lines.append("| Run id | Predictions | BET rate | Skip rate | Avg quality | Avg edge | Provider degradation |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for run in result.live_runs:
        lines.append(
            f"| {run.run_id} | {run.prediction_count} | {run.active_bet_rate:.2%} | {run.skip_rate:.2%} | "
            f"{run.average_source_quality:.2%} | {run.average_edge:.2%} | {run.provider_degradation_rate:.2%} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_stability_json_report(
    result: StabilityReviewResult,
    path: Path = DEFAULT_STABILITY_JSON_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "baseline": {
            "created_at": result.baseline.created_at.isoformat(),
            "model_version": result.baseline.model_version,
            "replay_phase1_ready": result.baseline.replay_phase1_ready,
            "replay_roi": result.baseline.replay_roi,
            "replay_average_clv": result.baseline.replay_average_clv,
            "replay_average_edge": result.baseline.replay_average_edge,
            "replay_average_source_quality": result.baseline.replay_average_source_quality,
            "replay_bet_count": result.baseline.replay_bet_count,
            "live_runs_considered": result.baseline.live_runs_considered,
            "live_average_prediction_count": result.baseline.live_average_prediction_count,
            "live_average_active_bet_rate": result.baseline.live_average_active_bet_rate,
            "live_average_skip_rate": result.baseline.live_average_skip_rate,
            "live_average_source_quality": result.baseline.live_average_source_quality,
            "live_average_expected_value": result.baseline.live_average_expected_value,
            "live_average_edge": result.baseline.live_average_edge,
            "live_average_provider_degradation_rate": result.baseline.live_average_provider_degradation_rate,
            "live_schedule_fallback_rate": result.baseline.live_schedule_fallback_rate,
        },
        "baseline_path": result.baseline_path,
        "drift": {
            "status": result.drift.status,
            "live_runs_considered": result.drift.live_runs_considered,
            "graded_predictions": result.drift.graded_predictions,
            "retraining_recommended": result.drift.retraining_recommended,
            "reasons": list(result.drift.reasons),
            "signals": [
                {
                    "name": signal.name,
                    "baseline_value": signal.baseline_value,
                    "current_value": signal.current_value,
                    "delta": signal.delta,
                    "threshold": signal.threshold,
                    "triggered": signal.triggered,
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
                }
                for market in result.readiness.markets
            ],
            "analyst": {
                "status": result.readiness.analyst.status,
                "predictor_authority": result.readiness.analyst.predictor_authority,
                "analyst_logging_enabled": result.readiness.analyst.analyst_logging_enabled,
                "note": result.readiness.analyst.note,
            },
        },
        "model_catalog": result.model_catalog,
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
                "provider_degradation_rate": run.provider_degradation_rate,
                "schedule_fallback_used": run.schedule_fallback_used,
            }
            for run in result.live_runs
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
