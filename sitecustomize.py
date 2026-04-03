from __future__ import annotations

import sys
from pathlib import Path


def _inject_workspace_packages() -> None:
    package_root = Path(__file__).resolve().parent / ".python_packages"
    package_text = str(package_root)
    if package_root.exists() and package_text not in sys.path:
        sys.path.insert(0, package_text)


_inject_workspace_packages()
