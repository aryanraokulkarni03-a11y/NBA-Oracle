from __future__ import annotations

import os

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


def get_env_value(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value not in {None, ""}:
        return value.strip()

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
