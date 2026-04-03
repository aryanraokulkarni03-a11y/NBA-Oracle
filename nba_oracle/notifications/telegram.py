from __future__ import annotations

from typing import Any

from nba_oracle.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.notifications.formatters import format_health_digest, format_history_digest, format_pick_card
from nba_oracle.runtime.health import build_health_snapshot, load_latest_live_report, load_latest_stability_report
from nba_oracle.runtime.state import record_notification_event


def send_telegram_message(
    text: str,
    *,
    event_type: str = "generic_message",
    chat_id: str | None = None,
) -> dict[str, object]:
    destination = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not destination:
        raise RuntimeError("telegram_not_configured")

    try:
        payload, _ = request_json(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            method="POST",
            json_body={
                "chat_id": destination,
                "text": text,
            },
            timeout=20,
        )
        record_notification_event(
            "telegram",
            event_type,
            True,
            destination,
            {"text_preview": text[:120]},
        )
        return payload if isinstance(payload, dict) else {"ok": True}
    except HttpRequestError as exc:
        record_notification_event(
            "telegram",
            event_type,
            False,
            destination,
            {"error": str(exc), "text_preview": text[:120]},
        )
        raise RuntimeError(f"telegram_send_failed:{exc}") from exc


def send_pick_card(prediction: dict[str, Any], *, event_type: str = "pick_card") -> dict[str, object]:
    return send_telegram_message(format_pick_card(prediction), event_type=event_type)


def send_live_digest(*, event_type: str = "live_digest") -> dict[str, object]:
    report = load_latest_live_report()
    predictions = report.get("predictions", [])
    if not predictions:
        return send_telegram_message("NBA Oracle Live Slate\nNo predictions available.", event_type=event_type)
    lines = ["NBA Oracle Live Slate"]
    for item in predictions[:10]:
        lines.append(f"{item.get('game_id')}: {item.get('selected_team')} | {item.get('decision')}")
    return send_telegram_message("\n".join(lines), event_type=event_type)


def handle_telegram_command(command_text: str) -> str:
    normalized = command_text.strip().split(maxsplit=1)[0].lower()
    if normalized == "/health":
        return format_health_digest(build_health_snapshot())
    if normalized == "/picks":
        report = load_latest_live_report()
        predictions = report.get("predictions", [])
        if predictions:
            return format_pick_card(predictions[0])
        return "NBA Oracle Pick Card\nNo picks available."
    if normalized == "/stats":
        stability = load_latest_stability_report()
        drift = stability.get("drift", {}) if isinstance(stability, dict) else {}
        return "\n".join(
            [
                "NBA Oracle Stats",
                f"Drift: {drift.get('status', 'n/a')}",
                f"Graded bets: {drift.get('outcome_metrics', {}).get('graded_bet_count', 0)}",
                f"Average CLV: {drift.get('outcome_metrics', {}).get('average_clv', 'n/a')}",
            ]
        )
    if normalized == "/history":
        report = load_latest_live_report()
        runs = []
        if report:
            predictions = report.get("predictions", [])
            runs.append(
                {
                    "run_id": report.get("run_id"),
                    "bet_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "BET"),
                    "lean_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "LEAN"),
                    "skip_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "SKIP"),
                }
            )
        return format_history_digest(runs)
    if normalized == "/result":
        stability = load_latest_stability_report()
        learning = build_health_snapshot().get("latest_learning") or {}
        return "\n".join(
            [
                "NBA Oracle Result Summary",
                f"Latest drift: {stability.get('drift', {}).get('status', 'n/a') if isinstance(stability, dict) else 'n/a'}",
                f"Learning: {learning.get('status', 'n/a')}",
            ]
        )
    return "Unknown Telegram command. Supported: /health /picks /stats /history /result"
