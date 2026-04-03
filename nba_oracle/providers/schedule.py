from __future__ import annotations

from datetime import datetime

from nba_oracle.config import HTTP_TIMEOUT_SECONDS, NBA_SCOREBOARD_URL
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.models import ProviderRecord, ProviderResponse, parse_dt
from nba_oracle.providers.base import BundleProvider
from nba_oracle.teams import build_game_id, compose_full_team_name

try:  # pragma: no cover - optional runtime path
    from nba_api.live.nba.endpoints import scoreboard as nba_scoreboard
except ImportError:  # pragma: no cover
    nba_scoreboard = None


class ScheduleProvider(BundleProvider):
    name = "nba_scoreboard_live"
    kind = "schedule"
    section_name = "schedule"

    def fetch_live(
        self,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        payload = None
        try:
            if nba_scoreboard is not None:
                payload = nba_scoreboard.ScoreBoard().get_dict()
            else:
                payload, _ = request_json(
                    NBA_SCOREBOARD_URL,
                    timeout=HTTP_TIMEOUT_SECONDS,
                )
        except HttpRequestError as exc:
            return self.degraded_response(
                decision_time,
                error=f"schedule_fetch_failed:{exc}",
                raw_payload={},
                trust=0.0,
            )

        games = _extract_games(payload)
        records: list[ProviderRecord] = []
        latest_source_time = decision_time
        for game in games:
            tipoff_raw = game.get("gameTimeUTC") or game.get("gameEt")
            if not tipoff_raw:
                continue

            tipoff_time = parse_dt(str(tipoff_raw))
            latest_source_time = max(latest_source_time, tipoff_time)
            if tipoff_time < decision_time:
                continue

            away_team = _team_name(dict(game.get("awayTeam", {})))
            home_team = _team_name(dict(game.get("homeTeam", {})))
            game_id = build_game_id(tipoff_time, away_team, home_team)
            records.append(
                ProviderRecord(
                    game_id=game_id,
                    data={
                        "game_id": game_id,
                        "away_team": away_team,
                        "home_team": home_team,
                        "tipoff_time": tipoff_time.isoformat(),
                        "away_team_id": game.get("awayTeam", {}).get("teamId"),
                        "home_team_id": game.get("homeTeam", {}).get("teamId"),
                        "away_team_abbr": game.get("awayTeam", {}).get("teamTricode"),
                        "home_team_abbr": game.get("homeTeam", {}).get("teamTricode"),
                        "game_status": game.get("gameStatus"),
                        "decision_time_candidate": decision_time.isoformat(),
                    },
                )
            )

        return self.build_response(
            source_time=latest_source_time,
            source_version="scoreboard-v1",
            trust=0.99,
            success=True,
            degraded=False,
            records=tuple(records),
            raw_payload={"games": games},
            error=None,
        )


def _extract_games(payload: dict[str, object] | list[object]) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        scoreboard = payload.get("scoreboard")
        if isinstance(scoreboard, dict) and isinstance(scoreboard.get("games"), list):
            return [dict(game) for game in scoreboard["games"]]
        if isinstance(payload.get("games"), list):
            return [dict(game) for game in payload["games"]]
    return []


def _team_name(team_payload: dict[str, object]) -> str:
    city = str(team_payload.get("teamCity") or team_payload.get("city") or "").strip()
    nickname = str(team_payload.get("teamName") or team_payload.get("nickname") or "").strip()
    if city and nickname:
        return compose_full_team_name(city, nickname)
    full_name = str(team_payload.get("teamTricode") or team_payload.get("name") or "").strip()
    return full_name
