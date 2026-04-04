from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    ORACLE_ALLOWED_ORIGINS,
    ORACLE_DEPLOYMENT_TARGET,
    ORACLE_FAILURE_ALERT_POLICY,
    ORACLE_LOCAL_AUTOSTART_MODE,
    ORACLE_LOCAL_DASHBOARD_BEHAVIOR,
    ORACLE_PASSWORD_HASH,
    ORACLE_PUBLIC_API_BASE_URL,
    ORACLE_SECRET_KEY,
    ODDS_API_KEY,
    REPORTS_DIR,
    ROOT_DIR,
    RUNTIME_DIR,
    RUNTIME_STATE_DIR,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    GMAIL_APP_PASSWORD,
    GMAIL_RECIPIENT,
    GMAIL_SENDER,
)


def build_startup_sanity_report() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    _ensure_directory(REPORTS_DIR)
    _ensure_directory(RUNTIME_DIR)
    _ensure_directory(RUNTIME_STATE_DIR)
    hosted_launcher_path = ROOT_DIR / "start_hosted_stack.bat"
    scheduler_script_path = ROOT_DIR / "scripts" / "run_nba_oracle_scheduler.ps1"
    scheduler_task_name = "NBA Oracle Scheduler"

    checks.append(
        _check(
            "deployment_target",
            "healthy" if ORACLE_DEPLOYMENT_TARGET == "vercel-cloudflare-supabase" else "warning",
            f"target={ORACLE_DEPLOYMENT_TARGET}",
        )
    )
    checks.append(
        _check(
            "public_api_base_url",
            "healthy" if ORACLE_PUBLIC_API_BASE_URL else "warning",
            ORACLE_PUBLIC_API_BASE_URL or "not_set_for_hosted_frontend",
        )
    )
    checks.append(
        _check(
            "allowed_origins",
            "healthy" if ORACLE_ALLOWED_ORIGINS else "failed",
            ",".join(ORACLE_ALLOWED_ORIGINS) if ORACLE_ALLOWED_ORIGINS else "missing",
        )
    )
    checks.append(
        _check(
            "supabase",
            "healthy" if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY else "failed",
            "configured" if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY else "missing_supabase_credentials",
        )
    )
    checks.append(
        _check(
            "odds_api",
            "healthy" if ODDS_API_KEY else "failed",
            "configured" if ODDS_API_KEY else "missing_odds_api_key",
        )
    )
    checks.append(
        _check(
            "auth_bootstrap",
            "healthy" if ORACLE_PASSWORD_HASH and ORACLE_SECRET_KEY else "failed",
            "configured" if ORACLE_PASSWORD_HASH and ORACLE_SECRET_KEY else "missing_password_hash_or_secret",
        )
    )
    checks.append(
        _check(
            "telegram_delivery",
            "healthy" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "warning",
            "configured" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "missing_telegram_config",
        )
    )
    checks.append(
        _check(
            "gmail_delivery",
            "healthy" if GMAIL_SENDER and GMAIL_APP_PASSWORD and GMAIL_RECIPIENT else "warning",
            "configured" if GMAIL_SENDER and GMAIL_APP_PASSWORD and GMAIL_RECIPIENT else "missing_gmail_config",
        )
    )
    checks.append(
        _check(
            "local_runtime_cache",
            "healthy" if (ROOT_DIR / ".python_packages").exists() else "warning",
            "present" if (ROOT_DIR / ".python_packages").exists() else "bootstrap_runtime_recommended",
        )
    )
    checks.append(
        _check(
            "hosted_launcher",
            "healthy" if hosted_launcher_path.exists() else "warning",
            "present" if hosted_launcher_path.exists() else "missing_start_hosted_stack_bat",
        )
    )
    checks.append(
        _check(
            "scheduler_runner_script",
            "healthy" if scheduler_script_path.exists() else "warning",
            "present" if scheduler_script_path.exists() else "missing_run_nba_oracle_scheduler_script",
        )
    )
    scheduler_task_registered = _scheduled_task_registered(scheduler_task_name)
    checks.append(
        _check(
            "scheduler_task",
            "healthy" if scheduler_task_registered else "warning",
            scheduler_task_name if scheduler_task_registered else "not_registered",
        )
    )
    checks.append(
        _check(
            "dashboard_build",
            "healthy" if (ROOT_DIR / "dashboard" / "dist" / "index.html").exists() else "warning",
            "present" if (ROOT_DIR / "dashboard" / "dist" / "index.html").exists() else "run_dashboard_build_before_deploy",
        )
    )
    checks.append(
        _check(
            "local_autostart_mode",
            "healthy" if ORACLE_LOCAL_AUTOSTART_MODE else "warning",
            ORACLE_LOCAL_AUTOSTART_MODE or "manual",
        )
    )
    checks.append(
        _check(
            "local_dashboard_behavior",
            "healthy" if ORACLE_LOCAL_DASHBOARD_BEHAVIOR else "warning",
            ORACLE_LOCAL_DASHBOARD_BEHAVIOR or "manual",
        )
    )
    checks.append(
        _check(
            "failure_alert_policy",
            "healthy" if ORACLE_FAILURE_ALERT_POLICY else "warning",
            ORACLE_FAILURE_ALERT_POLICY or "telegram-primary",
        )
    )

    failed = [item for item in checks if item["status"] == "failed"]
    warnings = [item for item in checks if item["status"] == "warning"]
    overall = "ready" if not failed and not warnings else "warning" if not failed else "failed"

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": overall,
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "deployment": {
            "target": ORACLE_DEPLOYMENT_TARGET,
            "public_api_base_url": ORACLE_PUBLIC_API_BASE_URL or None,
            "allowed_origins": list(ORACLE_ALLOWED_ORIGINS),
            "local_autostart_mode": ORACLE_LOCAL_AUTOSTART_MODE,
            "local_dashboard_behavior": ORACLE_LOCAL_DASHBOARD_BEHAVIOR,
            "failure_alert_policy": ORACLE_FAILURE_ALERT_POLICY,
        },
        "checks": checks,
    }


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _scheduled_task_registered(task_name: str) -> bool:
    try:
        result = subprocess.run(
            ["schtasks.exe", "/Query", "/TN", task_name],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0
