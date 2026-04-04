from __future__ import annotations

import json
from pathlib import Path

from nba_oracle.config import DEFAULT_JSON_REPORT_PATH, DEFAULT_REPORT_PATH, REPORTS_DIR
from nba_oracle.replay import ReplayReport


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_markdown_report(report: ReplayReport, path: Path = DEFAULT_REPORT_PATH) -> Path:
    ensure_reports_dir()
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 1 Replay Report")
    lines.append("")
    lines.append(f"- Fixture: `{report.fixture_path}`")
    lines.append(f"- Total games: `{report.total_games}`")
    lines.append(f"- BET count: `{report.bet_count}`")
    lines.append(f"- LEAN count: `{report.lean_count}`")
    lines.append(f"- SKIP count: `{report.skip_count}`")
    lines.append(f"- Hit rate: `{report.hit_rate:.2%}`")
    lines.append(f"- ROI: `{report.roi:.2%}`")
    lines.append(f"- Average CLV: `{report.average_clv:.2%}`")
    lines.append(f"- Average edge vs Stake: `{report.average_edge:.2%}`")
    lines.append(f"- Average source quality: `{report.average_source_quality:.2%}`")
    lines.append(f"- Average Stake-best gap: `{report.average_stake_to_best_gap:.2%}`")
    lines.append(f"- Average Stake-close gap: `{report.average_stake_to_close_gap:.2%}`")
    lines.append(f"- Phase 1 readiness: `{report.phase1_ready}`")
    lines.append("")
    lines.append("## Readiness Gates")
    lines.append("")
    lines.append(f"- Calibration gate: `{report.calibration_assessment.status}`")
    lines.append(f"- Actionable predictions: `{report.calibration_assessment.actionable_count}`")
    lines.append(f"- Populated calibration bins: `{report.calibration_assessment.populated_bins}`")
    lines.append(f"- Mean calibration gap: `{report.calibration_assessment.mean_absolute_gap:.2%}`")
    lines.append(f"- Max calibration gap: `{report.calibration_assessment.max_absolute_gap:.2%}`")
    for reason in report.calibration_assessment.reasons:
        lines.append(f"- Calibration note: `{reason}`")
    lines.append("")
    lines.append("## Calibration")
    lines.append("")
    lines.append("| Bin | Count | Avg probability | Hit rate | Abs gap |")
    lines.append("|---|---:|---:|---:|---:|")
    for bucket in report.calibration_bins:
        lines.append(
            f"| {bucket.label} | {bucket.count} | {bucket.average_probability:.2%} | "
            f"{bucket.hit_rate:.2%} | {bucket.absolute_gap:.2%} |"
        )
    lines.append("")
    lines.append("## Source Audit Summary")
    lines.append("")
    lines.append("| Source | Kind | Samples | Avg freshness | Avg trust | Avg quality | Avg age (min) | Avg signal delta |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for row in report.source_audit:
        lines.append(
            f"| {row.name} | {row.kind} | {row.samples} | {row.average_freshness:.2%} | "
            f"{row.average_trust:.2%} | {row.average_quality:.2%} | {row.average_age_minutes:.2f} | "
            f"{row.average_signal_delta:.2%} |"
        )
    lines.append("")
    lines.append("## Skip Reasons")
    lines.append("")
    if report.skip_reasons:
        for reason, count in sorted(report.skip_reasons.items()):
            lines.append(f"- `{reason}`: {count}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Decisions")
    lines.append("")
    lines.append(
        "| Game | Team | Decision | Model prob | Stake line | Best line | Close line | "
        "Stake prob | Best prob | Close prob | Market prior | Timing adj | Uncertainty | Segment | EV | Edge | Source quality | Reasons |"
    )
    lines.append(
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|"
    )
    for prediction in report.predictions:
        reason_text = ", ".join(prediction.reasons)
        lines.append(
            f"| {prediction.game_id} | {prediction.selected_team} | {prediction.decision} | "
            f"{prediction.model_probability:.2%} | {prediction.stake_american} | "
            f"{prediction.best_american} | {prediction.close_american} | "
            f"{prediction.stake_probability:.2%} | {prediction.best_probability:.2%} | "
            f"{prediction.close_probability:.2%} | {prediction.market_prior_probability:.2%} | "
            f"{prediction.timing_adjustment:.2%} | {prediction.uncertainty:.2%} | {prediction.market_segment} | {prediction.expected_value:.2%} | "
            f"{prediction.edge_vs_stake:.2%} | {prediction.source_quality:.2%} | {reason_text} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_json_report(report: ReplayReport, path: Path = DEFAULT_JSON_REPORT_PATH) -> Path:
    ensure_reports_dir()
    payload = {
        "fixture_path": str(report.fixture_path),
        "total_games": report.total_games,
        "bet_count": report.bet_count,
        "lean_count": report.lean_count,
        "skip_count": report.skip_count,
        "hit_rate": report.hit_rate,
        "roi": report.roi,
        "average_clv": report.average_clv,
        "average_edge": report.average_edge,
        "average_source_quality": report.average_source_quality,
        "average_stake_to_best_gap": report.average_stake_to_best_gap,
        "average_stake_to_close_gap": report.average_stake_to_close_gap,
        "phase1_ready": report.phase1_ready,
        "calibration_assessment": {
            "status": report.calibration_assessment.status,
            "actionable_count": report.calibration_assessment.actionable_count,
            "populated_bins": report.calibration_assessment.populated_bins,
            "mean_absolute_gap": report.calibration_assessment.mean_absolute_gap,
            "max_absolute_gap": report.calibration_assessment.max_absolute_gap,
            "reasons": list(report.calibration_assessment.reasons),
        },
        "calibration_bins": [
            {
                "label": bucket.label,
                "count": bucket.count,
                "average_probability": bucket.average_probability,
                "hit_rate": bucket.hit_rate,
                "absolute_gap": bucket.absolute_gap,
            }
            for bucket in report.calibration_bins
        ],
        "source_audit": [
            {
                "name": row.name,
                "kind": row.kind,
                "samples": row.samples,
                "average_freshness": row.average_freshness,
                "average_trust": row.average_trust,
                "average_quality": row.average_quality,
                "average_age_minutes": row.average_age_minutes,
                "average_signal_delta": row.average_signal_delta,
            }
            for row in report.source_audit
        ],
        "skip_reasons": report.skip_reasons,
        "predictions": [
            {
                "game_id": item.game_id,
                "selected_team": item.selected_team,
                "decision": item.decision,
                "stake_american": item.stake_american,
                "best_american": item.best_american,
                "close_american": item.close_american,
                "model_probability": item.model_probability,
                "market_prior_probability": item.market_prior_probability,
                "source_adjustment": item.source_adjustment,
                "timing_adjustment": item.timing_adjustment,
                "uncertainty": item.uncertainty,
                "market_segment": item.market_segment,
                "stake_probability": item.stake_probability,
                "best_probability": item.best_probability,
                "close_probability": item.close_probability,
                "expected_value": item.expected_value,
                "edge_vs_stake": item.edge_vs_stake,
                "source_quality": item.source_quality,
                "source_scores": [
                    {
                        "name": score.name,
                        "kind": score.kind,
                        "freshness": score.freshness,
                        "trust": score.trust,
                        "quality": score.quality,
                        "age_minutes": score.age_minutes,
                        "signal_delta": score.signal_delta,
                    }
                    for score in item.source_scores
                ],
                "reasons": list(item.reasons),
                "actual_winner": item.actual_winner,
            }
            for item in report.predictions
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
