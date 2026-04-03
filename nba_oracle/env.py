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


def upsert_dotenv_values(values: dict[str, str], env_path: Path | None = None) -> Path:
    target = env_path or (Path(__file__).resolve().parent.parent / ".env")
    existing: dict[str, str] = {}
    order: list[str] = []
    if target.exists():
        for raw_line in target.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            existing[key] = value.strip()
            order.append(key)

    for key, value in values.items():
        if key not in order:
            order.append(key)
        existing[key] = value

    rendered = [f"{key}={existing[key]}" for key in order]
    target.write_text("\n".join(rendered) + "\n", encoding="utf-8")
    _load_dotenv.cache_clear()
    return target
