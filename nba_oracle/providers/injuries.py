from __future__ import annotations

import html
import re
from datetime import datetime

from nba_oracle.config import ESPN_NBA_INJURIES_URL, HTTP_TIMEOUT_SECONDS
from nba_oracle.http import HttpRequestError, request_text
from nba_oracle.models import ProviderRecord, ProviderResponse
from nba_oracle.providers.base import BundleProvider
from nba_oracle.teams import TEAM_METADATA, canonicalize_team_name

STATUS_WEIGHTS = {
    "out": 1.0,
    "doubtful": 0.75,
    "questionable": 0.55,
    "day-to-day": 0.35,
    "probable": 0.1,
}


class InjuryProvider(BundleProvider):
    name = "espn_injuries"
    kind = "injury"
    section_name = "injuries"

    def fetch_live(
        self,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        schedule = context.get("schedule")
        if schedule is None:
            return self.degraded_response(
                decision_time,
                error="schedule_context_missing",
                raw_payload={},
            )
        if not schedule.records:
            return self.build_response(
                source_time=decision_time,
                source_version="espn-injuries-v1",
                trust=0.85,
                success=True,
                degraded=False,
                records=tuple(),
                raw_payload={"team_count": 0},
                error=None,
            )

        try:
            payload, _ = request_text(
                ESPN_NBA_INJURIES_URL,
                timeout=HTTP_TIMEOUT_SECONDS,
            )
        except HttpRequestError as exc:
            return self.degraded_response(
                decision_time,
                error=f"injury_fetch_failed:{exc}",
                raw_payload={},
                trust=0.0,
            )

        sections = _extract_team_sections(payload)
        if not sections:
            return self.degraded_response(
                decision_time,
                error="injury_page_parse_failed",
                raw_payload={"html_length": len(payload)},
                trust=0.0,
            )

        odds = context.get("odds")
        records: list[ProviderRecord] = []
        for schedule_row in schedule.record_map.values():
            away_team = canonicalize_team_name(str(schedule_row["away_team"]))
            home_team = canonicalize_team_name(str(schedule_row["home_team"]))
            selected_team = away_team
            if odds and schedule_row["game_id"] in odds.record_map:
                selected_team = canonicalize_team_name(str(odds.record_map[schedule_row["game_id"]]["selected_team"]))
            opponent_team = home_team if selected_team == away_team else away_team

            selected_summary = _summarize_team(sections.get(selected_team, []))
            opponent_summary = _summarize_team(sections.get(opponent_team, []))
            signal_delta = max(min((opponent_summary["severity"] - selected_summary["severity"]) * 0.015, 0.04), -0.04)

            records.append(
                ProviderRecord(
                    game_id=str(schedule_row["game_id"]),
                    data={
                        "game_id": schedule_row["game_id"],
                        "signal_delta": round(signal_delta, 4),
                        "summary": (
                            f"{selected_team} injury load {selected_summary['major_flags']} major flags "
                            f"vs {opponent_team} {opponent_summary['major_flags']} major flags"
                        ),
                        "confirmation_level": "reported",
                        "selected_team_flags": selected_summary["total_flags"],
                        "opponent_team_flags": opponent_summary["total_flags"],
                    },
                )
            )

        return self.build_response(
            source_time=decision_time,
            source_version="espn-injuries-v1",
            trust=0.85,
            success=True,
            degraded=False,
            records=tuple(records),
            raw_payload={"team_count": len(sections)},
            error=None,
        )


def _extract_team_sections(payload: str) -> dict[str, list[str]]:
    cleaned = re.sub(r"<script\b[^>]*>.*?</script>", " ", payload, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style\b[^>]*>.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"</(p|div|tr|td|th|li|section|article|table|tbody|thead|h1|h2|h3|h4|h5|h6|br)>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    lines = [
        re.sub(r"\s+", " ", html.unescape(line)).strip()
        for line in cleaned.splitlines()
    ]
    lines = [line for line in lines if line]

    sections: dict[str, list[str]] = {}
    current_team: str | None = None
    valid_teams = set(TEAM_METADATA)
    for line in lines:
        canonical = canonicalize_team_name(line)
        if canonical in valid_teams:
            current_team = canonical
            sections.setdefault(current_team, [])
            continue
        if current_team is None:
            continue
        if line.lower().startswith("data provided by"):
            current_team = None
            continue
        sections[current_team].append(line)
    return sections


def _summarize_team(lines: list[str]) -> dict[str, float | int]:
    severity = 0.0
    total_flags = 0
    major_flags = 0
    for line in lines:
        normalized = line.lower()
        if normalized not in STATUS_WEIGHTS:
            continue
        total_flags += 1
        weight = STATUS_WEIGHTS[normalized]
        severity += weight
        if weight >= STATUS_WEIGHTS["questionable"]:
            major_flags += 1
    return {
        "severity": severity,
        "total_flags": total_flags,
        "major_flags": major_flags,
    }
