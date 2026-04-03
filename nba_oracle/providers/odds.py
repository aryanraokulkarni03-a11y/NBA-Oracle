from __future__ import annotations

from datetime import datetime

from nba_oracle.config import (
    HTTP_TIMEOUT_SECONDS,
    ODDS_API_BASE_URL,
    ODDS_API_KEY,
    ODDS_API_MARKETS,
    ODDS_API_ODDS_FORMAT,
    ODDS_API_REGIONS,
    ODDS_API_SPORT,
    ODDS_REFERENCE_BOOKMAKER,
)
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.market import american_to_probability
from nba_oracle.models import ProviderRecord, ProviderResponse
from nba_oracle.providers.base import BundleProvider
from nba_oracle.teams import canonicalize_team_name


def _price_rank(price: int) -> float:
    if price > 0:
        return price / 100
    return 100 / abs(price)


class OddsProvider(BundleProvider):
    name = "the_odds_api"
    kind = "odds"
    section_name = "odds"

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
                source_version="the-odds-api-v4",
                trust=0.95,
                success=True,
                degraded=False,
                records=tuple(),
                raw_payload={"events": []},
                error=None,
            )
        if not ODDS_API_KEY:
            return self.degraded_response(
                decision_time,
                error="odds_api_key_missing",
                raw_payload={},
            )

        try:
            payload, _ = request_json(
                f"{ODDS_API_BASE_URL}/sports/{ODDS_API_SPORT}/odds",
                params={
                    "regions": ODDS_API_REGIONS,
                    "markets": ODDS_API_MARKETS,
                    "oddsFormat": ODDS_API_ODDS_FORMAT,
                    "apiKey": ODDS_API_KEY,
                },
                timeout=HTTP_TIMEOUT_SECONDS,
            )
        except HttpRequestError as exc:
            return self.degraded_response(
                decision_time,
                error=f"odds_fetch_failed:{exc}",
                raw_payload={},
                trust=0.0,
            )

        events = [dict(item) for item in payload] if isinstance(payload, list) else []
        event_map = {
            (
                canonicalize_team_name(str(event.get("away_team", ""))),
                canonicalize_team_name(str(event.get("home_team", ""))),
            ): event
            for event in events
        }

        records: list[ProviderRecord] = []
        missing_games = 0
        for schedule_row in schedule.record_map.values():
            away_team = canonicalize_team_name(str(schedule_row["away_team"]))
            home_team = canonicalize_team_name(str(schedule_row["home_team"]))
            event = event_map.get((away_team, home_team))
            if event is None:
                missing_games += 1
                continue

            normalized_probs, team_prices = _extract_market_view(event, away_team, home_team)
            if not normalized_probs:
                missing_games += 1
                continue

            selected_team = max(normalized_probs, key=normalized_probs.get)
            selected_prices = team_prices[selected_team]
            reference_bookmaker = _select_reference_bookmaker(selected_prices)
            stake_american = selected_prices[reference_bookmaker]
            best_american = max(selected_prices.values(), key=_price_rank)
            records.append(
                ProviderRecord(
                    game_id=str(schedule_row["game_id"]),
                    data={
                        "game_id": schedule_row["game_id"],
                        "selected_team": selected_team,
                        "stake_american": stake_american,
                        "best_american": best_american,
                        "close_american": stake_american,
                        "opening_american": None,
                        "consensus_probability": round(normalized_probs[selected_team], 4),
                        "signal_delta": 0.0,
                        "line_move": "unavailable_live_snapshot",
                        "reference_bookmaker": reference_bookmaker,
                        "book_count": len(selected_prices),
                        "market_timestamp": event.get("commence_time"),
                    },
                )
            )

        success = bool(records)
        degraded = missing_games > 0 or not success
        error = None
        if not success:
            error = "no_odds_records_built"
        elif missing_games > 0:
            error = f"missing_odds_for_{missing_games}_games"

        return self.build_response(
            source_time=decision_time,
            source_version="the-odds-api-v4",
            trust=0.95 if success else 0.0,
            success=success,
            degraded=degraded,
            records=tuple(records),
            raw_payload={"events": events},
            error=error,
        )


def _extract_market_view(
    event: dict[str, object],
    away_team: str,
    home_team: str,
) -> tuple[dict[str, float], dict[str, dict[str, int]]]:
    probabilities: dict[str, list[float]] = {away_team: [], home_team: []}
    prices: dict[str, dict[str, int]] = {away_team: {}, home_team: {}}

    for bookmaker in event.get("bookmakers", []) or []:
        bookmaker_payload = dict(bookmaker)
        bookmaker_key = str(bookmaker_payload.get("key") or bookmaker_payload.get("title") or "unknown")
        h2h_market = next(
            (
                dict(market)
                for market in bookmaker_payload.get("markets", []) or []
                if market.get("key") == "h2h"
            ),
            None,
        )
        if h2h_market is None:
            continue

        outcome_map: dict[str, int] = {}
        for outcome in h2h_market.get("outcomes", []) or []:
            outcome_payload = dict(outcome)
            team_name = canonicalize_team_name(str(outcome_payload.get("name", "")))
            if team_name not in probabilities:
                continue
            price = int(outcome_payload["price"])
            outcome_map[team_name] = price
            prices[team_name][bookmaker_key] = price

        if away_team not in outcome_map or home_team not in outcome_map:
            continue

        away_prob = american_to_probability(outcome_map[away_team])
        home_prob = american_to_probability(outcome_map[home_team])
        total = away_prob + home_prob
        probabilities[away_team].append(away_prob / total)
        probabilities[home_team].append(home_prob / total)

    normalized = {
        team_name: (sum(values) / len(values)) if values else 0.0
        for team_name, values in probabilities.items()
    }
    return normalized, prices

def _select_reference_bookmaker(prices: dict[str, int]) -> str:
    if ODDS_REFERENCE_BOOKMAKER and ODDS_REFERENCE_BOOKMAKER in prices:
        return ODDS_REFERENCE_BOOKMAKER
    return sorted(prices.keys())[0]
