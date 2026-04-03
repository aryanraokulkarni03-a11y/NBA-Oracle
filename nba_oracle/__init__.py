"""NBA Oracle backend package."""

from __future__ import annotations

import site
import sys
from pathlib import Path


def _ensure_workspace_packages() -> None:
    workspace_packages = Path(__file__).resolve().parent.parent / ".python_packages"
    workspace_text = str(workspace_packages)
    if workspace_packages.exists() and workspace_text not in sys.path:
        sys.path.insert(0, workspace_text)


def _ensure_user_site() -> None:
    try:
        user_site = str(Path(site.getusersitepackages()))
    except Exception:
        return
    if user_site not in sys.path:
        sys.path.append(user_site)


_ensure_workspace_packages()
_ensure_user_site()
