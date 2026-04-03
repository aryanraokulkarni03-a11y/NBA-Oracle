from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


@lru_cache(maxsize=1)
def _load_dotenv() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_env_value(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value not in {None, ""}:
        return value.strip()

    dotenv_value = _load_dotenv().get(name)
    if dotenv_value not in {None, ""}:
        return dotenv_value.strip()

    if winreg is None:
        return default

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
    except OSError:
        return default

    if value in {None, ""}:
        return default
    return str(value).strip()
