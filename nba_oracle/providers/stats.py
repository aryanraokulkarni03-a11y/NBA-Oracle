from __future__ import annotations

from datetime import datetime

from nba_oracle.config import (
    HTTP_TIMEOUT_SECONDS,
    NBA_TEAM_ESTIMATED_METRICS_URL,
)
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.models import ProviderRecord, ProviderResponse
from nba_oracle.providers.base import BundleProvider
from nba_oracle.teams import canonicalize_team_name, season_string_for_date

try:  # pragma: no cover - optional runtime path
    from nba_api.stats.endpoints import teamestimatedmetrics as nba_teamestimatedmetrics
except ImportError:  # pragma: no cover
    nba_teamestimatedmetrics = None

NBA_STATS_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
    "User-Agent": "Mozilla/5.0",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}


class StatsProvider(BundleProvider):
    name = "nba_team_estimated_metrics"
    kind = "stats"
    section_name = "stats"

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
                source_version="teamestimatedmetrics-v1",
                trust=0.91,
                success=True,
                degraded=False,
                records=tuple(),
                raw_payload={"row_count": 0},
                error=None,
            )

        try:
            if nba_teamestimatedmetrics is not None:
                payload = nba_teamestimatedmetrics.TeamEstimatedMetrics(
                    league_id="00",
                    season=season_string_for_date(decision_time),
                    season_type="Regular Season",
                ).get_dict()
            else:
                payload, _ = request_json(
                    NBA_TEAM_ESTIMATED_METRICS_URL,
                    params={
                        "LeagueID": "00",
                        "Season": season_string_for_date(decision_time),
                        "SeasonType": "Regular Season",
                    },
                    headers=NBA_STATS_HEADERS,
                    timeout=HTTP_TIMEOUT_SECONDS,
                )
        except Exception as exc:
            return self.degraded_response(
                decision_time,
                error=f"stats_fetch_failed:{exc}",
                raw_payload={},
                trust=0.0,
            )

        team_rows = _extract_rows(payload)
        if not team_rows:
            return self.degraded_response(
                decision_time,
                error="stats_payload_empty",
                raw_payload={"payload": payload},
                trust=0.0,
            )

        team_map = {
            canonicalize_team_name(str(row.get("TEAM_NAME", ""))): row
            for row in team_rows
        }
        odds = context.get("odds")
        records: list[ProviderRecord] = []
        missing_games = 0
        for schedule_row in schedule.record_map.values():
            away_team = canonicalize_team_name(str(schedule_row["away_team"]))
            home_team = canonicalize_team_name(str(schedule_row["home_team"]))
            away_stats = team_map.get(away_team)
            home_stats = team_map.get(home_team)
            if away_stats is None or home_stats is None:
                missing_games += 1
                continue

            selected_team = _selected_team(schedule_row["game_id"], away_team, home_team, odds)
            opponent_team = home_team if selected_team == away_team else away_team
            selected_stats = away_stats if selected_team == away_team else home_stats
            opponent_stats = home_stats if selected_team == away_team else away_stats

            selected_net = _to_float(selected_stats.get("E_NET_RATING"))
            opponent_net = _to_float(opponent_stats.get("E_NET_RATING"))
            selected_win_pct = _to_float(selected_stats.get("W_PCT"))
            opponent_win_pct = _to_float(opponent_stats.get("W_PCT"))
            selected_pace = _to_float(selected_stats.get("E_PACE"))
            opponent_pace = _to_float(opponent_stats.get("E_PACE"))
            selected_offense = _to_float(selected_stats.get("E_OFF_RATING"))
            opponent_offense = _to_float(opponent_stats.get("E_OFF_RATING"))
            selected_defense = _to_float(selected_stats.get("E_DEF_RATING"))
            opponent_defense = _to_float(opponent_stats.get("E_DEF_RATING"))

            net_diff = selected_net - opponent_net
            win_pct_diff = selected_win_pct - opponent_win_pct
            pace_diff = selected_pace - opponent_pace
            off_rating_diff = selected_offense - opponent_offense
            defense_edge = opponent_defense - selected_defense
            team_strength_score = (
                (net_diff * 0.55)
                + (win_pct_diff * 20)
                + (off_rating_diff * 0.12)
                + (defense_edge * 0.14)
                + (pace_diff * 0.03)
            )
            signal_delta = max(
                min(
                    (net_diff * 0.0015)
                    + (win_pct_diff * 0.055)
                    + (off_rating_diff * 0.0005)
                    + (defense_edge * 0.0006)
                    + (pace_diff * 0.0002),
                    0.04,
                ),
                -0.04,
            )

            records.append(
                ProviderRecord(
                    game_id=str(schedule_row["game_id"]),
                    data={
                        "game_id": schedule_row["game_id"],
                        "signal_delta": round(signal_delta, 4),
                        "summary": (
                            f"{selected_team} metrics edge: net {net_diff:+.2f}, "
                            f"win_pct {win_pct_diff:+.3f}, defense {defense_edge:+.2f}"
                        ),
                        "rest_edge": 0,
                        "selected_team_net_rating": round(selected_net, 3),
                        "opponent_net_rating": round(opponent_net, 3),
                        "selected_team": selected_team,
                        "opponent_team": opponent_team,
                        "net_rating_diff": round(net_diff, 3),
                        "win_pct_diff": round(win_pct_diff, 4),
                        "pace_diff": round(pace_diff, 3),
                        "off_rating_diff": round(off_rating_diff, 3),
                        "defense_edge": round(defense_edge, 3),
                        "team_strength_score": round(team_strength_score, 3),
                    },
                )
            )

        success = bool(records)
        degraded = missing_games > 0 or not success
        error = None
        if not success:
            error = "no_stats_records_built"
        elif missing_games > 0:
            error = f"missing_stats_for_{missing_games}_games"

        return self.build_response(
            source_time=decision_time,
            source_version="teamestimatedmetrics-v1",
            trust=0.91 if success else 0.0,
            success=success,
            degraded=degraded,
            records=tuple(records),
            raw_payload={"row_count": len(team_rows)},
            error=error,
        )


def _extract_rows(payload: dict[str, object] | list[object]) -> list[dict[str, object]]:
    result_sets = []
    if isinstance(payload, dict):
        if isinstance(payload.get("resultSets"), list):
            result_sets = payload["resultSets"]
        elif isinstance(payload.get("resultSet"), dict):
            result_sets = [payload["resultSet"]]

    if not result_sets:
        return []

    first_set = dict(result_sets[0])
    headers = list(first_set.get("headers", []))
    rows = list(first_set.get("rowSet", []))
    if not headers or not rows:
        return []
    return [dict(zip(headers, row)) for row in rows]


def _selected_team(
    game_id: str,
    away_team: str,
    home_team: str,
    odds: ProviderResponse | None,
) -> str:
    if odds and game_id in odds.record_map:
        return canonicalize_team_name(str(odds.record_map[game_id]["selected_team"]))
    return away_team


def _to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
