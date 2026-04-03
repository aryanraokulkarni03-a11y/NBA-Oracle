from __future__ import annotations

import re
from datetime import date, datetime


TEAM_METADATA = {
    "Atlanta Hawks": {"abbr": "ATL", "city": "Atlanta", "nickname": "Hawks"},
    "Boston Celtics": {"abbr": "BOS", "city": "Boston", "nickname": "Celtics"},
    "Brooklyn Nets": {"abbr": "BKN", "city": "Brooklyn", "nickname": "Nets"},
    "Charlotte Hornets": {"abbr": "CHA", "city": "Charlotte", "nickname": "Hornets"},
    "Chicago Bulls": {"abbr": "CHI", "city": "Chicago", "nickname": "Bulls"},
    "Cleveland Cavaliers": {"abbr": "CLE", "city": "Cleveland", "nickname": "Cavaliers"},
    "Dallas Mavericks": {"abbr": "DAL", "city": "Dallas", "nickname": "Mavericks"},
    "Denver Nuggets": {"abbr": "DEN", "city": "Denver", "nickname": "Nuggets"},
    "Detroit Pistons": {"abbr": "DET", "city": "Detroit", "nickname": "Pistons"},
    "Golden State Warriors": {"abbr": "GSW", "city": "Golden State", "nickname": "Warriors"},
    "Houston Rockets": {"abbr": "HOU", "city": "Houston", "nickname": "Rockets"},
    "Indiana Pacers": {"abbr": "IND", "city": "Indiana", "nickname": "Pacers"},
    "Los Angeles Clippers": {"abbr": "LAC", "city": "Los Angeles", "nickname": "Clippers"},
    "Los Angeles Lakers": {"abbr": "LAL", "city": "Los Angeles", "nickname": "Lakers"},
    "Memphis Grizzlies": {"abbr": "MEM", "city": "Memphis", "nickname": "Grizzlies"},
    "Miami Heat": {"abbr": "MIA", "city": "Miami", "nickname": "Heat"},
    "Milwaukee Bucks": {"abbr": "MIL", "city": "Milwaukee", "nickname": "Bucks"},
    "Minnesota Timberwolves": {"abbr": "MIN", "city": "Minnesota", "nickname": "Timberwolves"},
    "New Orleans Pelicans": {"abbr": "NOP", "city": "New Orleans", "nickname": "Pelicans"},
    "New York Knicks": {"abbr": "NYK", "city": "New York", "nickname": "Knicks"},
    "Oklahoma City Thunder": {"abbr": "OKC", "city": "Oklahoma City", "nickname": "Thunder"},
    "Orlando Magic": {"abbr": "ORL", "city": "Orlando", "nickname": "Magic"},
    "Philadelphia 76ers": {"abbr": "PHI", "city": "Philadelphia", "nickname": "76ers"},
    "Phoenix Suns": {"abbr": "PHX", "city": "Phoenix", "nickname": "Suns"},
    "Portland Trail Blazers": {"abbr": "POR", "city": "Portland", "nickname": "Trail Blazers"},
    "Sacramento Kings": {"abbr": "SAC", "city": "Sacramento", "nickname": "Kings"},
    "San Antonio Spurs": {"abbr": "SAS", "city": "San Antonio", "nickname": "Spurs"},
    "Toronto Raptors": {"abbr": "TOR", "city": "Toronto", "nickname": "Raptors"},
    "Utah Jazz": {"abbr": "UTA", "city": "Utah", "nickname": "Jazz"},
    "Washington Wizards": {"abbr": "WAS", "city": "Washington", "nickname": "Wizards"},
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


_ALIASES: dict[str, str] = {}
for canonical_name, meta in TEAM_METADATA.items():
    city = meta["city"]
    nickname = meta["nickname"]
    abbreviation = meta["abbr"]
    for alias in {
        canonical_name,
        f"{city} {nickname}",
        nickname,
        abbreviation,
        abbreviation.lower(),
    }:
        _ALIASES[_slug(alias)] = canonical_name

_ALIASES[_slug("LA Clippers")] = "Los Angeles Clippers"
_ALIASES[_slug("LA Lakers")] = "Los Angeles Lakers"


def canonicalize_team_name(value: str) -> str:
    cleaned = value.strip()
    return _ALIASES.get(_slug(cleaned), cleaned)


def team_abbreviation(value: str) -> str:
    canonical_name = canonicalize_team_name(value)
    meta = TEAM_METADATA.get(canonical_name)
    if not meta:
        raise KeyError(f"Unknown NBA team name: {value}")
    return str(meta["abbr"])


def compose_full_team_name(city: str, nickname: str) -> str:
    raw = f"{city} {nickname}".strip()
    return canonicalize_team_name(raw)


def build_game_id(game_date: date | datetime, away_team: str, home_team: str) -> str:
    game_day = game_date.date() if isinstance(game_date, datetime) else game_date
    away = team_abbreviation(away_team).lower()
    home = team_abbreviation(home_team).lower()
    return f"{game_day.isoformat()}-{away}-{home}"


def season_string_for_date(value: datetime) -> str:
    start_year = value.year if value.month >= 10 else value.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"
