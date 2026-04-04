from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from nba_oracle.config import HTTP_TIMEOUT_SECONDS, NBA_SCOREBOARD_URL, NBA_SCOREBOARD_V2_URL
from nba_oracle.http import HttpRequestError, request_json, request_text
from nba_oracle.providers.stats import NBA_STATS_HEADERS
from nba_oracle.teams import build_game_id, canonicalize_team_name, compose_full_team_name


OFFICIAL_OUTCOME_FETCH_RETRIES = 3
OFFICIAL_OUTCOME_FETCH_BACKOFF_SECONDS = 2
OFFICIAL_OUTCOME_HTTP_TIMEOUT_SECONDS = max(HTTP_TIMEOUT_SECONDS, 45)


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
    if _is_live_scoreboard_payload(payload):
        return _build_outcomes_from_live_scoreboard(payload, game_date)

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
    last_error: HttpRequestError | None = None
    for attempt in range(1, OFFICIAL_OUTCOME_FETCH_RETRIES + 1):
        try:
            body, _ = request_text(
                NBA_SCOREBOARD_V2_URL,
                params={
                    "GameDate": game_date.strftime("%m/%d/%Y"),
                    "LeagueID": "00",
                    "DayOffset": 0,
                },
                headers=NBA_STATS_HEADERS,
                timeout=OFFICIAL_OUTCOME_HTTP_TIMEOUT_SECONDS,
            )
            break
        except HttpRequestError as exc:
            last_error = exc
            if attempt < OFFICIAL_OUTCOME_FETCH_RETRIES:
                time.sleep(OFFICIAL_OUTCOME_FETCH_BACKOFF_SECONDS * attempt)
    else:
        return _request_live_scoreboard_fallback(game_date, last_error)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"official_outcome_payload_invalid:{game_date.isoformat()}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"official_outcome_payload_invalid:{game_date.isoformat()}")
    return payload


def _request_live_scoreboard_fallback(
    game_date: date,
    last_error: HttpRequestError | None,
) -> dict[str, object]:
    try:
        payload, _ = request_json(
            NBA_SCOREBOARD_URL,
            timeout=OFFICIAL_OUTCOME_HTTP_TIMEOUT_SECONDS,
        )
    except HttpRequestError as exc:
        detail = str(last_error or exc)
        raise RuntimeError(f"official_outcome_fetch_failed:{game_date.isoformat()}:{detail}") from exc

    if not isinstance(payload, dict):
        detail = str(last_error) if last_error else "live_scoreboard_payload_invalid"
        raise RuntimeError(f"official_outcome_fetch_failed:{game_date.isoformat()}:{detail}")
    if not _is_live_scoreboard_payload(payload):
        detail = str(last_error) if last_error else "live_scoreboard_payload_invalid"
        raise RuntimeError(f"official_outcome_fetch_failed:{game_date.isoformat()}:{detail}")
    return payload


def _is_live_scoreboard_payload(payload: dict[str, object]) -> bool:
    scoreboard = payload.get("scoreboard")
    return isinstance(scoreboard, dict) and isinstance(scoreboard.get("games"), list)


def _build_outcomes_from_live_scoreboard(
    payload: dict[str, object],
    game_date: date,
) -> tuple[OfficialOutcome, ...]:
    scoreboard = payload.get("scoreboard", {})
    games = scoreboard.get("games", []) if isinstance(scoreboard, dict) else []
    source_time = datetime.now(timezone.utc)
    outcomes: list[OfficialOutcome] = []

    for item in games:
        game = dict(item) if isinstance(item, dict) else {}
        tipoff_text = str(game.get("gameTimeUTC") or "")
        if not tipoff_text:
            continue
        tipoff_time = _parse_game_time(tipoff_text)
        if tipoff_time is None or tipoff_time.date() != game_date:
            continue

        game_status = str(game.get("gameStatusText") or game.get("gameStatus") or "")
        game_status_id = _to_int(game.get("gameStatus"))
        if game_status_id != 3 and "final" not in game_status.lower():
            continue

        away_team_payload = dict(game.get("awayTeam", {}))
        home_team_payload = dict(game.get("homeTeam", {}))
        away_team = _team_name_from_live_team(away_team_payload)
        home_team = _team_name_from_live_team(home_team_payload)
        away_score = _to_int(away_team_payload.get("score"))
        home_score = _to_int(home_team_payload.get("score"))
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
                source_name="nba_scoreboard_live",
                source_version="scoreboard-live-v1",
                source_time=source_time,
            )
        )

    return tuple(outcomes)


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


def _team_name_from_live_team(team_payload: dict[str, object]) -> str | None:
    city = str(team_payload.get("teamCity") or team_payload.get("city") or "").strip()
    nickname = str(team_payload.get("teamName") or team_payload.get("nickname") or "").strip()
    abbreviation = str(team_payload.get("teamTricode") or team_payload.get("tricode") or "").strip()

    if city and nickname:
        return compose_full_team_name(city, nickname)
    if abbreviation:
        return canonicalize_team_name(abbreviation)
    return None


def _parse_game_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _to_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
