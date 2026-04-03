from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from nba_oracle.config import (
    AUTH_DIR,
    ORACLE_API_RATE_LIMIT_PER_MINUTE,
    ORACLE_AUTH_LOCKOUT_SECONDS,
    ORACLE_AUTH_MAX_FAILED_ATTEMPTS,
)


AUTH_STATE_PATH = AUTH_DIR / "auth_state.json"
AUTH_LOG_PATH = AUTH_DIR / "auth_log.txt"


@dataclass(frozen=True)
class AuthDecision:
    allowed: bool
    reason: str
    retry_after_seconds: int = 0


def ensure_auth_dir() -> None:
    AUTH_DIR.mkdir(parents=True, exist_ok=True)


def log_auth_event(event: str, *, actor: str, detail: str = "") -> None:
    ensure_auth_dir()
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"{timestamp} | {event} | {actor} | {detail}".rstrip()
    with AUTH_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def record_failed_login(actor: str) -> AuthDecision:
    state = _load_auth_state()
    now = datetime.now(timezone.utc)
    entry = state.setdefault(actor, {"failures": [], "requests": []})
    entry["failures"] = [
        timestamp
        for timestamp in entry.get("failures", [])
        if now - _parse_dt(timestamp) <= timedelta(seconds=ORACLE_AUTH_LOCKOUT_SECONDS)
    ]
    entry["failures"].append(now.isoformat())
    _save_auth_state(state)
    if len(entry["failures"]) >= ORACLE_AUTH_MAX_FAILED_ATTEMPTS:
        return AuthDecision(False, "locked_out", ORACLE_AUTH_LOCKOUT_SECONDS)
    return AuthDecision(False, "invalid_credentials", 0)


def clear_failed_logins(actor: str) -> None:
    state = _load_auth_state()
    entry = state.get(actor)
    if entry is not None:
        entry["failures"] = []
        _save_auth_state(state)


def check_login_allowed(actor: str) -> AuthDecision:
    state = _load_auth_state()
    now = datetime.now(timezone.utc)
    entry = state.setdefault(actor, {"failures": [], "requests": []})
    recent_failures = [
        timestamp
        for timestamp in entry.get("failures", [])
        if now - _parse_dt(timestamp) <= timedelta(seconds=ORACLE_AUTH_LOCKOUT_SECONDS)
    ]
    entry["failures"] = recent_failures
    _save_auth_state(state)
    if len(recent_failures) >= ORACLE_AUTH_MAX_FAILED_ATTEMPTS:
        most_recent = _parse_dt(recent_failures[-1])
        retry_after = max(
            1,
            int((most_recent + timedelta(seconds=ORACLE_AUTH_LOCKOUT_SECONDS) - now).total_seconds()),
        )
        return AuthDecision(False, "locked_out", retry_after)
    return AuthDecision(True, "allowed", 0)


def check_rate_limit(actor: str, *, limit: int = ORACLE_API_RATE_LIMIT_PER_MINUTE) -> AuthDecision:
    state = _load_auth_state()
    now = datetime.now(timezone.utc)
    entry = state.setdefault(actor, {"failures": [], "requests": []})
    entry["requests"] = [
        timestamp
        for timestamp in entry.get("requests", [])
        if now - _parse_dt(timestamp) <= timedelta(minutes=1)
    ]
    if len(entry["requests"]) >= limit:
        oldest = _parse_dt(entry["requests"][0])
        retry_after = max(1, int((oldest + timedelta(minutes=1) - now).total_seconds()))
        _save_auth_state(state)
        return AuthDecision(False, "rate_limited", retry_after)
    entry["requests"].append(now.isoformat())
    _save_auth_state(state)
    return AuthDecision(True, "allowed", 0)


def _load_auth_state() -> dict[str, dict[str, list[str]]]:
    ensure_auth_dir()
    if not AUTH_STATE_PATH.exists():
        return {}
    try:
        return json.loads(AUTH_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_auth_state(state: dict[str, dict[str, list[str]]]) -> None:
    ensure_auth_dir()
    AUTH_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
