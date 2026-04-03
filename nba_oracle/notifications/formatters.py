from __future__ import annotations

from typing import Any


def format_pick_card(item: dict[str, Any]) -> str:
    reasons = item.get("reasons") or []
    reason_text = ", ".join(str(reason) for reason in reasons[:3]) if isinstance(reasons, list) else ""
    return "\n".join(
        [
            "NBA Oracle Pick Card",
            f"Game: {item.get('game_id')}",
            f"Team: {item.get('selected_team')}",
            f"Decision: {item.get('decision')}",
            f"EV: {float(item.get('expected_value', 0.0)):.2%}",
            f"Edge: {float(item.get('edge_vs_stake', 0.0)):.2%}",
            f"Reasons: {reason_text or 'n/a'}",
        ]
    )


def format_live_digest(report: dict[str, Any]) -> str:
    lines = ["NBA Oracle Live Slate"]
    run_id = report.get("run_id")
    if run_id:
        lines.append(f"Run: {run_id}")
    predictions = report.get("predictions", [])
    for item in predictions[:10]:
        lines.append(
            f"{item.get('game_id')}: {item.get('selected_team')} | {item.get('decision')} | "
            f"EV {float(item.get('expected_value', 0.0)):.2%}"
        )
    if not predictions:
        lines.append("No predictions available.")
    return "\n".join(lines)


def format_health_digest(snapshot: dict[str, Any]) -> str:
    lines = ["NBA Oracle Health"]
    live = snapshot.get("latest_live") or {}
    stability = snapshot.get("latest_stability") or {}
    learning = snapshot.get("latest_learning") or {}
    outcomes = snapshot.get("latest_outcomes") or {}
    lines.append(f"Live run: {live.get('run_id') or 'n/a'}")
    lines.append(f"Predictions: {live.get('prediction_count') or 0}")
    lines.append(f"Drift: {stability.get('drift_status') or 'n/a'}")
    lines.append(f"Timing: {stability.get('timing_status') or 'n/a'}")
    lines.append(f"Learning: {learning.get('status') or 'n/a'}")
    lines.append(f"Pending outcomes: {outcomes.get('pending_unfinished') or 0}")
    return "\n".join(lines)


def format_email(subject: str, body: str) -> tuple[str, str]:
    return subject.strip(), body.strip()


def format_history_digest(runs: list[dict[str, Any]]) -> str:
    lines = ["NBA Oracle History"]
    for item in runs[:5]:
        lines.append(
            f"{item.get('run_id')}: bets {item.get('bet_count', 0)} | "
            f"leans {item.get('lean_count', 0)} | skips {item.get('skip_count', 0)}"
        )
    if len(lines) == 1:
        lines.append("No history available.")
    return "\n".join(lines)
