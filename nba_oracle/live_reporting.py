from __future__ import annotations

import json
from pathlib import Path

from nba_oracle.config import DEFAULT_LIVE_JSON_REPORT_PATH, DEFAULT_LIVE_REPORT_PATH, REPORTS_DIR
from nba_oracle.models import LiveRunResult


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_live_markdown_report(
    result: LiveRunResult,
    path: Path = DEFAULT_LIVE_REPORT_PATH,
) -> Path:
    ensure_reports_dir()
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 2 Live Slate Report")
    lines.append("")
    lines.append(f"- Run id: `{result.run_id}`")
    lines.append(f"- Decision time: `{result.decision_time.isoformat()}`")
    lines.append(f"- Storage mode: `{result.storage_mode}`")
    lines.append(f"- Provider count: `{len(result.providers)}`")
    lines.append(f"- Snapshot count: `{len(result.snapshots)}`")
    lines.append(f"- Prediction count: `{len(result.predictions)}`")
    lines.append("")
    lines.append("## Provider Health")
    lines.append("")
    lines.append("| Provider | Kind | Success | Degraded | Source time | Version | Trust | Error |")
    lines.append("|---|---|---|---|---|---|---:|---|")
    for provider in result.providers:
        lines.append(
            f"| {provider.name} | {provider.kind} | {provider.success} | {provider.degraded} | "
            f"{provider.source_time.isoformat()} | {provider.source_version} | {provider.trust:.2f} | "
            f"{provider.error or ''} |"
        )
    lines.append("")
    lines.append("## Decisions")
    lines.append("")
    lines.append(
        "| Game | Team | Decision | Model prob | Reference book | Reference line | Best line | Close line | "
        "Reference prob | Best prob | Close prob | EV | Edge vs reference | Source quality | Reasons |"
    )
    lines.append(
        "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    )
    for prediction in result.predictions:
        lines.append(
            f"| {prediction.game_id} | {prediction.selected_team} | {prediction.decision} | "
            f"{prediction.model_probability:.2%} | {prediction.reference_bookmaker} | {prediction.stake_american} | {prediction.best_american} | "
            f"{prediction.close_american} | {prediction.stake_probability:.2%} | {prediction.best_probability:.2%} | "
            f"{prediction.close_probability:.2%} | {prediction.expected_value:.2%} | {prediction.edge_vs_stake:.2%} | "
            f"{prediction.source_quality:.2%} | {', '.join(prediction.reasons)} |"
        )
    lines.append("")
    lines.append("## Stored Artifacts")
    lines.append("")
    for stored_path in result.stored_paths:
        lines.append(f"- `{stored_path}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_live_json_report(
    result: LiveRunResult,
    path: Path = DEFAULT_LIVE_JSON_REPORT_PATH,
) -> Path:
    ensure_reports_dir()
    payload = {
        "run_id": result.run_id,
        "decision_time": result.decision_time.isoformat(),
        "storage_mode": result.storage_mode,
        "providers": [
            {
                "name": provider.name,
                "kind": provider.kind,
                "source_time": provider.source_time.isoformat(),
                "source_version": provider.source_version,
                "trust": provider.trust,
                "success": provider.success,
                "degraded": provider.degraded,
                "record_count": len(provider.records),
                "error": provider.error,
            }
            for provider in result.providers
        ],
        "predictions": [
            {
                "game_id": item.game_id,
                "selected_team": item.selected_team,
                "decision": item.decision,
                "reference_bookmaker": item.reference_bookmaker,
                "stake_american": item.stake_american,
                "best_american": item.best_american,
                "close_american": item.close_american,
                "opening_american": item.opening_american,
                "market_timestamp": item.market_timestamp.isoformat() if item.market_timestamp else None,
                "model_probability": item.model_probability,
                "stake_probability": item.stake_probability,
                "best_probability": item.best_probability,
                "close_probability": item.close_probability,
                "expected_value": item.expected_value,
                "edge_vs_stake": item.edge_vs_stake,
                "source_quality": item.source_quality,
                "reasons": list(item.reasons),
            }
            for item in result.predictions
        ],
        "stored_paths": list(result.stored_paths),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
