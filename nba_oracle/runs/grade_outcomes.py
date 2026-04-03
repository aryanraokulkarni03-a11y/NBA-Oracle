from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from nba_oracle.config import RUNTIME_DIR
from nba_oracle.outcomes.fetcher import OfficialOutcome, fetch_official_outcomes
from nba_oracle.outcomes.persistence import build_outcome_repository
from nba_oracle.outcomes.reporting import OutcomeGradeRecord, OutcomeGradingResult
from nba_oracle.teams import build_game_id


def grade_outcomes(
    *,
    runtime_dir: Path = RUNTIME_DIR,
    as_of: datetime | None = None,
    limit: int | None = None,
) -> OutcomeGradingResult:
    resolved_as_of = as_of or datetime.now(timezone.utc)
    run_dirs = _load_run_dirs(runtime_dir, limit=limit)

    run_candidates: dict[str, dict[str, object]] = {}
    dates_needed: set[date] = set()
    eligible_predictions = 0
    already_graded = 0
    pending_unfinished = 0

    for run_dir in run_dirs:
        run_state = _load_run_state(run_dir)
        if run_state is None:
            continue

        eligible_records: list[dict[str, object]] = []
        for snapshot, prediction in run_state["pairs"]:
            actual_winner = prediction.get("actual_winner")
            tipoff_time = datetime.fromisoformat(str(snapshot["tipoff_time"]).replace("Z", "+00:00"))
            if actual_winner not in {None, ""}:
                already_graded += 1
                continue
            if tipoff_time > resolved_as_of:
                pending_unfinished += 1
                continue

            eligible_predictions += 1
            dates_needed.add(tipoff_time.date())
            eligible_records.append(
                {
                    "snapshot": snapshot,
                    "prediction": prediction,
                    "tipoff_time": tipoff_time,
                }
            )

        if eligible_records:
            run_candidates[run_dir.name] = {
                "run_dir": run_dir,
                "predictions_payload": run_state["predictions_payload"],
                "snapshots_payload": run_state["snapshots_payload"],
                "eligible_records": eligible_records,
            }

    official_outcomes = _load_official_outcomes(dates_needed)
    repository = build_outcome_repository()
    grades: list[OutcomeGradeRecord] = []
    stored_paths: list[str] = []
    missing_official_outcomes = 0

    for run_id, candidate in run_candidates.items():
        run_grades: list[OutcomeGradeRecord] = []
        predictions_changed = False
        snapshots_changed = False

        for record in candidate["eligible_records"]:
            snapshot = record["snapshot"]
            prediction = record["prediction"]
            tipoff_time = record["tipoff_time"]
            lookup_key = build_game_id(tipoff_time, str(snapshot["away_team"]), str(snapshot["home_team"]))
            official = official_outcomes.get(lookup_key)
            if official is None:
                missing_official_outcomes += 1
                continue

            prediction["actual_winner"] = official.actual_winner
            snapshot["actual_winner"] = official.actual_winner
            predictions_changed = True
            snapshots_changed = True

            grade = OutcomeGradeRecord(
                run_id=run_id,
                game_id=str(prediction["game_id"]),
                away_team=str(snapshot["away_team"]),
                home_team=str(snapshot["home_team"]),
                selected_team=str(prediction.get("selected_team", "")),
                decision=str(prediction.get("decision", "")),
                actual_winner=official.actual_winner,
                won=str(prediction.get("selected_team", "")) == official.actual_winner,
                tipoff_time=tipoff_time,
                graded_at=resolved_as_of,
                game_status=official.game_status,
                source_name=official.source_name,
                source_version=official.source_version,
            )
            run_grades.append(grade)
            grades.append(grade)

        if predictions_changed:
            predictions_path = Path(candidate["run_dir"]) / "predictions.json"
            predictions_path.write_text(
                json.dumps(candidate["predictions_payload"], indent=2),
                encoding="utf-8",
            )
            stored_paths.append(str(predictions_path))

        if snapshots_changed:
            snapshots_path = Path(candidate["run_dir"]) / "snapshots.json"
            snapshots_path.write_text(
                json.dumps(candidate["snapshots_payload"], indent=2),
                encoding="utf-8",
            )
            stored_paths.append(str(snapshots_path))

        if run_grades:
            stored_paths.append(repository.store_grades(run_id, tuple(run_grades)))

    return OutcomeGradingResult(
        runtime_dir=runtime_dir,
        graded_at=resolved_as_of,
        evaluated_runs=len(run_dirs),
        eligible_predictions=eligible_predictions,
        newly_graded=len(grades),
        already_graded=already_graded,
        pending_unfinished=pending_unfinished,
        missing_official_outcomes=missing_official_outcomes,
        grades=tuple(grades),
        stored_paths=tuple(stored_paths),
    )


def _load_run_dirs(runtime_dir: Path, *, limit: int | None) -> tuple[Path, ...]:
    if not runtime_dir.exists():
        return ()
    run_dirs = sorted(
        (path for path in runtime_dir.iterdir() if path.is_dir() and path.name.startswith("live-")),
        key=lambda item: item.name,
        reverse=True,
    )
    if limit is not None:
        run_dirs = run_dirs[:limit]
    return tuple(sorted(run_dirs, key=lambda item: item.name))


def _load_run_state(run_dir: Path) -> dict[str, object] | None:
    predictions_path = run_dir / "predictions.json"
    snapshots_path = run_dir / "snapshots.json"
    if not predictions_path.exists() or not snapshots_path.exists():
        return None

    try:
        predictions_payload = json.loads(predictions_path.read_text(encoding="utf-8"))
        snapshots_payload = json.loads(snapshots_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    prediction_map = {
        str(item.get("game_id")): item
        for item in predictions_payload.get("predictions", [])
        if item.get("game_id")
    }
    pairs: list[tuple[dict[str, object], dict[str, object]]] = []
    for snapshot in snapshots_payload.get("snapshots", []):
        game_id = str(snapshot.get("game_id") or "")
        prediction = prediction_map.get(game_id)
        if prediction is None:
            continue
        pairs.append((snapshot, prediction))

    return {
        "predictions_payload": predictions_payload,
        "snapshots_payload": snapshots_payload,
        "pairs": pairs,
    }


def _load_official_outcomes(dates_needed: set[date]) -> dict[str, OfficialOutcome]:
    outcomes_by_game_id: dict[str, OfficialOutcome] = {}
    for game_date in sorted(dates_needed):
        for outcome in fetch_official_outcomes(game_date):
            outcomes_by_game_id[outcome.game_id] = outcome
    return outcomes_by_game_id
