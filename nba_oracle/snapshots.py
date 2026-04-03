from __future__ import annotations

import json
from pathlib import Path

from nba_oracle.models import GameSnapshot


class SnapshotValidationError(ValueError):
    """Raised when a snapshot violates point-in-time rules."""


def load_game_snapshots(path: Path) -> list[GameSnapshot]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    games = [GameSnapshot.from_dict(item) for item in payload["games"]]
    for game in games:
        validate_game_snapshot(game)
    return games


def validate_game_snapshot(game: GameSnapshot) -> None:
    if game.decision_time >= game.tipoff_time:
        raise SnapshotValidationError(
            f"{game.game_id}: decision_time must be before tipoff_time"
        )
    for source in game.sources:
        if source.source_time > game.decision_time:
            raise SnapshotValidationError(
                f"{game.game_id}: source '{source.name}' leaks future data"
            )

