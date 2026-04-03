from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from nba_oracle.config import HTTP_TIMEOUT_SECONDS, NBA_SCOREBOARD_V2_URL
from nba_oracle.http import HttpRequestError, request_text
from nba_oracle.providers.stats import NBA_STATS_HEADERS
from nba_oracle.teams import build_game_id, canonicalize_team_name, compose_full_team_name


@dataclass(frozen=True)
class OfficialOutcome:
    game_id: str
    game_date: date
    away_team: str
    home_team: str
    away_score: int
    home_score: int
    actual_winner: str
    game_status: str
    source_name: str
    source_version: str
    source_time: datetime


def fetch_official_outcomes(game_date: date) -> tuple[OfficialOutcome, ...]:
    payload = _request_scoreboard(game_date)
    game_headers = _extract_result_set_rows(payload, "GameHeader")
    line_scores = _extract_result_set_rows(payload, "LineScore")
    line_score_map = _group_rows(line_scores, "GAME_ID")

    source_time = datetime.now(timezone.utc)
    outcomes: list[OfficialOutcome] = []
    for header in game_headers:
        game_status = str(header.get("GAME_STATUS_TEXT") or header.get("GAME_STATUS") or "")
        game_status_id = _to_int(header.get("GAME_STATUS_ID"))
        if game_status_id != 3 and "final" not in game_status.lower():
            continue

        raw_game_id = str(header.get("GAME_ID") or "")
        if not raw_game_id:
            continue
        rows = line_score_map.get(raw_game_id, [])
        if len(rows) < 2:
            continue

        away_row, home_row = _resolve_line_score_sides(rows, header)
        if away_row is None or home_row is None:
            continue

        away_team = _team_name_from_line_score(away_row)
        home_team = _team_name_from_line_score(home_row)
        away_score = _to_int(away_row.get("PTS"))
        home_score = _to_int(home_row.get("PTS"))
        if away_team is None or home_team is None or away_score == home_score:
            continue

        actual_winner = away_team if away_score > home_score else home_team
        outcomes.append(
            OfficialOutcome(
                game_id=build_game_id(game_date, away_team, home_team),
                game_date=game_date,
                away_team=away_team,
                home_team=home_team,
                away_score=away_score,
                home_score=home_score,
                actual_winner=actual_winner,
                game_status=game_status or "Final",
                source_name="nba_scoreboard_v2",
                source_version="scoreboardv2-v1",
                source_time=source_time,
            )
        )

    return tuple(outcomes)


def _request_scoreboard(game_date: date) -> dict[str, object]:
    try:
        body, _ = request_text(
            NBA_SCOREBOARD_V2_URL,
            params={
                "GameDate": game_date.strftime("%m/%d/%Y"),
                "LeagueID": "00",
                "DayOffset": 0,
            },
            headers=NBA_STATS_HEADERS,
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except HttpRequestError as exc:
        raise RuntimeError(f"official_outcome_fetch_failed:{game_date.isoformat()}:{exc}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"official_outcome_payload_invalid:{game_date.isoformat()}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"official_outcome_payload_invalid:{game_date.isoformat()}")
    return payload


def _extract_result_set_rows(payload: dict[str, object], set_name: str) -> list[dict[str, object]]:
    result_sets = payload.get("resultSets")
    if isinstance(result_sets, list):
        for item in result_sets:
            result_set = dict(item)
            if str(result_set.get("name")) != set_name:
                continue
            headers = list(result_set.get("headers", []))
            rows = list(result_set.get("rowSet", []))
            if not headers:
                return []
            return [dict(zip(headers, row)) for row in rows]

    result_set = payload.get("resultSet")
    if isinstance(result_set, dict) and set_name == "GameHeader":
        headers = list(result_set.get("headers", []))
        rows = list(result_set.get("rowSet", []))
        return [dict(zip(headers, row)) for row in rows]

    return []


def _group_rows(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        value = str(row.get(key) or "")
        if not value:
            continue
        grouped.setdefault(value, []).append(row)
    return grouped


def _resolve_line_score_sides(
    rows: list[dict[str, object]],
    header: dict[str, object],
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    home_id = str(header.get("HOME_TEAM_ID") or "")
    away_id = str(header.get("VISITOR_TEAM_ID") or "")

    away_row = next((row for row in rows if str(row.get("TEAM_ID") or "") == away_id), None)
    home_row = next((row for row in rows if str(row.get("TEAM_ID") or "") == home_id), None)
    if away_row is not None and home_row is not None:
        return away_row, home_row

    if len(rows) == 2:
        return rows[0], rows[1]
    return None, None


def _team_name_from_line_score(row: dict[str, object]) -> str | None:
    city = str(row.get("TEAM_CITY_NAME") or row.get("TEAM_CITY") or "").strip()
    nickname = str(
        row.get("TEAM_NICKNAME")
        or row.get("TEAM_NAME")
        or row.get("TEAM_SLUG")
        or ""
    ).strip()
    abbreviation = str(row.get("TEAM_ABBREVIATION") or "").strip()

    if city and nickname:
        return compose_full_team_name(city, nickname)
    if abbreviation:
        return canonicalize_team_name(abbreviation)
    return None


def _to_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
