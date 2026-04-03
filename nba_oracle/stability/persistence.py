from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    PHASE3_ANALYST_LOGS_TABLE,
    PHASE3_BASELINES_TABLE,
    PHASE3_MODEL_REVIEWS_TABLE,
    PHASE3_REVIEWS_TABLE,
    PHASE3_TIMING_EVENTS_TABLE,
    STABILITY_DIR,
    STORAGE_MODE,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)
from nba_oracle.http import HttpRequestError, request_json


class LocalStabilityRepository:
    storage_mode = "local"

    def __init__(self, root: Path = STABILITY_DIR) -> None:
        self.root = root

    def _write_json(self, name: str, payload: dict[str, object] | list[dict[str, object]]) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / name
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)

    def store_baseline(self, payload: dict[str, object]) -> str:
        return self._write_json("phase3_baseline.json", payload)

    def store_review(self, review_id: str, payload: dict[str, object]) -> str:
        return self._write_json(f"{review_id}_review.json", payload)

    def store_timing_events(self, review_id: str, payload: list[dict[str, object]]) -> str:
        return self._write_json(f"{review_id}_timing_events.json", payload)

    def store_analyst_logs(self, review_id: str, payload: list[dict[str, object]]) -> str:
        return self._write_json(f"{review_id}_analyst_logs.json", payload)

    def store_model_registry(self, payload: dict[str, object]) -> str:
        return self._write_json("phase3_model_registry.json", payload)

    def store_review_bundle(
        self,
        review_id: str,
        review_payload: dict[str, object],
        timing_events: list[dict[str, object]],
        analyst_logs: list[dict[str, object]],
        model_registry_payload: dict[str, object],
    ) -> list[str]:
        return [
            self.store_review(review_id, review_payload),
            self.store_timing_events(review_id, timing_events),
            self.store_analyst_logs(review_id, analyst_logs),
            self.store_model_registry(model_registry_payload),
        ]


class SupabaseStabilityRepository:
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

    def store_baseline(self, payload: dict[str, object]) -> str:
        if not self.enabled:
            return ""
        self._upsert_rows(
            PHASE3_BASELINES_TABLE,
            [
                {
                    "baseline_fingerprint": payload["baseline_fingerprint"],
                    "created_at": payload["created_at"],
                    "model_version": payload["model_version"],
                    "schema_version": payload["schema_version"],
                    "config_fingerprint": payload["config_fingerprint"],
                    "replay_report_fingerprint": payload["replay_report_fingerprint"],
                    "creation_reason": payload["creation_reason"],
                    "baseline_payload": payload,
                }
            ],
        )
        return f"supabase:{PHASE3_BASELINES_TABLE}:{payload['baseline_fingerprint']}"

    def store_review(self, review_id: str, payload: dict[str, object]) -> str:
        if not self.enabled:
            return ""
        self._upsert_rows(
            PHASE3_REVIEWS_TABLE,
            [
                {
                    "review_id": review_id,
                    "created_at": payload["created_at"],
                    "baseline_fingerprint": payload["baseline"]["baseline_fingerprint"],
                    "model_version": payload["model_catalog"]["model_version"],
                    "review_payload": payload,
                }
            ],
        )
        return f"supabase:{PHASE3_REVIEWS_TABLE}:{review_id}"

    def store_timing_events(self, review_id: str, payload: list[dict[str, object]]) -> str:
        if not self.enabled or not payload:
            return ""
        rows = [
            {
                "review_id": review_id,
                "game_id": row["game_id"],
                "event_type": row["event_type"],
                "source_kind": row["source_kind"],
                "source_name": row["source_name"],
                "event_payload": row,
            }
            for row in payload
        ]
        self._upsert_rows(PHASE3_TIMING_EVENTS_TABLE, rows)
        return f"supabase:{PHASE3_TIMING_EVENTS_TABLE}:{review_id}"

    def store_analyst_logs(self, review_id: str, payload: list[dict[str, object]]) -> str:
        if not self.enabled:
            return ""
        rows = [
            {
                "review_id": review_id,
                "game_id": row.get("game_id", "__summary__"),
                "disagreement_type": row["disagreement_type"],
                "final_authority": row["final_authority"],
                "log_payload": row,
            }
            for row in payload
        ] or [
            {
                "review_id": review_id,
                "game_id": "__summary__",
                "disagreement_type": "no_analyst_payload",
                "final_authority": "predictor",
                "log_payload": {"review_id": review_id, "disagreement_type": "no_analyst_payload"},
            }
        ]
        self._upsert_rows(PHASE3_ANALYST_LOGS_TABLE, rows)
        return f"supabase:{PHASE3_ANALYST_LOGS_TABLE}:{review_id}"

    def store_model_registry(self, payload: dict[str, object]) -> str:
        if not self.enabled:
            return ""
        self._upsert_rows(
            PHASE3_MODEL_REVIEWS_TABLE,
            [
                {
                    "review_id": payload["current_review_id"] or "__no_review__",
                    "created_at": payload["updated_at"],
                    "active_model_version": payload["active_model_version"],
                    "candidate_model_version": payload["candidate_model_version"],
                    "review_status": payload["review_status"],
                    "promotion_reason": payload["promotion_reason"],
                    "rollback_reason": payload["rollback_reason"],
                    "review_payload": payload,
                }
            ],
        )
        return f"supabase:{PHASE3_MODEL_REVIEWS_TABLE}:{payload['current_review_id'] or '__no_review__'}"

    def store_review_bundle(
        self,
        review_id: str,
        review_payload: dict[str, object],
        timing_events: list[dict[str, object]],
        analyst_logs: list[dict[str, object]],
        model_registry_payload: dict[str, object],
    ) -> list[str]:
        stored: list[str] = []
        for marker in (
            self.store_review(review_id, review_payload),
            self.store_timing_events(review_id, timing_events),
            self.store_analyst_logs(review_id, analyst_logs),
            self.store_model_registry(model_registry_payload),
        ):
            if marker:
                stored.append(marker)
        return stored

    def _upsert_rows(self, table: str, rows: list[dict[str, Any]]) -> None:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }
        try:
            request_json(
                f"{self.url}/rest/v1/{table}",
                method="POST",
                headers=headers,
                json_body=rows,
                timeout=20,
            )
        except HttpRequestError as exc:
            raise RuntimeError(f"supabase_insert_failed:{table}:{exc}") from exc


class DualStabilityRepository:
    storage_mode = "dual"

    def __init__(
        self,
        local_repository: LocalStabilityRepository | None = None,
        supabase_repository: SupabaseStabilityRepository | None = None,
    ) -> None:
        self.local_repository = local_repository or LocalStabilityRepository()
        self.supabase_repository = supabase_repository or SupabaseStabilityRepository()

    def store_baseline(self, payload: dict[str, object]) -> list[str]:
        stored = [self.local_repository.store_baseline(payload)]
        try:
            remote = self.supabase_repository.store_baseline(payload)
        except RuntimeError as exc:
            remote = f"supabase_error:{exc}"
        if remote:
            stored.append(remote)
        return stored

    def store_review_bundle(
        self,
        review_id: str,
        review_payload: dict[str, object],
        timing_events: list[dict[str, object]],
        analyst_logs: list[dict[str, object]],
        model_registry_payload: dict[str, object],
    ) -> list[str]:
        stored = [
            self.local_repository.store_review(review_id, review_payload),
            self.local_repository.store_timing_events(review_id, timing_events),
            self.local_repository.store_analyst_logs(review_id, analyst_logs),
            self.local_repository.store_model_registry(model_registry_payload),
        ]
        try:
            for marker in (
                self.supabase_repository.store_review(review_id, review_payload),
                self.supabase_repository.store_timing_events(review_id, timing_events),
                self.supabase_repository.store_analyst_logs(review_id, analyst_logs),
                self.supabase_repository.store_model_registry(model_registry_payload),
            ):
                if marker:
                    stored.append(marker)
        except RuntimeError as exc:
            stored.append(f"supabase_error:{exc}")
        return stored


def build_stability_repository(storage_mode: str | None = None) -> LocalStabilityRepository | SupabaseStabilityRepository | DualStabilityRepository:
    requested_mode = (storage_mode or STORAGE_MODE or "local").lower()
    if requested_mode == "supabase":
        return SupabaseStabilityRepository()
    if requested_mode == "dual":
        return DualStabilityRepository()
    return LocalStabilityRepository()
