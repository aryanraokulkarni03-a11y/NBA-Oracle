from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    DEFAULT_STORAGE_MODE,
    PHASE3_OUTCOME_GRADES_TABLE,
    RUNTIME_DIR,
    STORAGE_MODE,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.outcomes.reporting import OutcomeGradeRecord


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return _serialize(asdict(value))
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


class LocalOutcomeRepository:
    storage_mode = "local"

    def __init__(self, root: Path = RUNTIME_DIR) -> None:
        self.root = root

    def store_grades(self, run_id: str, grades: tuple[OutcomeGradeRecord, ...]) -> str:
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "outcome_grades.json"
        path.write_text(json.dumps({"grades": _serialize(grades)}, indent=2), encoding="utf-8")
        return str(path)


class SupabaseOutcomeRepository:
    storage_mode = "supabase"

    def __init__(
        self,
        *,
        url: str = SUPABASE_URL or "",
        service_role_key: str = SUPABASE_SERVICE_ROLE_KEY or "",
    ) -> None:
        self.url = url.rstrip("/")
        self.service_role_key = service_role_key
        self.enabled = bool(self.url and self.service_role_key)

    def store_grades(self, run_id: str, grades: tuple[OutcomeGradeRecord, ...]) -> str:
        if not self.enabled or not grades:
            return ""

        rows = [
            {
                "run_id": run_id,
                "game_id": grade.game_id,
                "actual_winner": grade.actual_winner,
                "selected_team": grade.selected_team,
                "decision": grade.decision,
                "won": grade.won,
                "game_status": grade.game_status,
                "source_name": grade.source_name,
                "source_version": grade.source_version,
                "tipoff_time": grade.tipoff_time.isoformat(),
                "graded_at": grade.graded_at.isoformat(),
                "grade_payload": _serialize(grade),
            }
            for grade in grades
        ]
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }
        try:
            request_json(
                f"{self.url}/rest/v1/{PHASE3_OUTCOME_GRADES_TABLE}",
                method="POST",
                params={"on_conflict": "run_id,game_id"},
                headers=headers,
                json_body=rows,
                timeout=20,
            )
        except HttpRequestError as exc:
            raise RuntimeError(f"supabase_insert_failed:{PHASE3_OUTCOME_GRADES_TABLE}:{exc}") from exc
        return f"supabase:{PHASE3_OUTCOME_GRADES_TABLE}:{run_id}"


class DualOutcomeRepository:
    storage_mode = "dual"

    def __init__(
        self,
        local_repository: LocalOutcomeRepository | None = None,
        supabase_repository: SupabaseOutcomeRepository | None = None,
    ) -> None:
        self.local_repository = local_repository or LocalOutcomeRepository()
        self.supabase_repository = supabase_repository or SupabaseOutcomeRepository()

    def store_grades(self, run_id: str, grades: tuple[OutcomeGradeRecord, ...]) -> str:
        local_path = self.local_repository.store_grades(run_id, grades)
        try:
            remote_path = self.supabase_repository.store_grades(run_id, grades)
        except RuntimeError as exc:
            remote_path = f"supabase_error:{exc}"
        return local_path if not remote_path else f"{local_path} | {remote_path}"


def build_outcome_repository(storage_mode: str | None = None):
    requested_mode = (storage_mode or STORAGE_MODE or DEFAULT_STORAGE_MODE).lower()
    if requested_mode == "supabase":
        return SupabaseOutcomeRepository()
    if requested_mode == "dual":
        return DualOutcomeRepository()
    return LocalOutcomeRepository()
