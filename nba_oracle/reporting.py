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
    lines.append("")
    lines.append("## Calibration")
    lines.append("")
    lines.append("| Bin | Count | Avg probability | Hit rate |")
    lines.append("|---|---:|---:|---:|")
    for bucket in report.calibration_bins:
        lines.append(
            f"| {bucket.label} | {bucket.count} | {bucket.average_probability:.2%} | {bucket.hit_rate:.2%} |"
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
    lines.append("| Game | Team | Decision | Model prob | Stake prob | EV | Edge | Source quality | Reasons |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    for prediction in report.predictions:
        reason_text = ", ".join(prediction.reasons)
        lines.append(
            f"| {prediction.game_id} | {prediction.selected_team} | {prediction.decision} | "
            f"{prediction.model_probability:.2%} | {prediction.stake_probability:.2%} | "
            f"{prediction.expected_value:.2%} | {prediction.edge_vs_stake:.2%} | "
            f"{prediction.source_quality:.2%} | {reason_text} |"
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
        "calibration_bins": [
            {
                "label": bucket.label,
                "count": bucket.count,
                "average_probability": bucket.average_probability,
                "hit_rate": bucket.hit_rate,
            }
            for bucket in report.calibration_bins
        ],
        "skip_reasons": report.skip_reasons,
        "predictions": [
            {
                "game_id": item.game_id,
                "selected_team": item.selected_team,
                "decision": item.decision,
                "model_probability": item.model_probability,
                "stake_probability": item.stake_probability,
                "best_probability": item.best_probability,
                "close_probability": item.close_probability,
                "expected_value": item.expected_value,
                "edge_vs_stake": item.edge_vs_stake,
                "source_quality": item.source_quality,
                "reasons": list(item.reasons),
                "actual_winner": item.actual_winner,
            }
            for item in report.predictions
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

