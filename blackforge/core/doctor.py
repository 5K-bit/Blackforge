from __future__ import annotations

import importlib.util
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from blackforge.core.manifest import MANIFEST_NAME


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_doctor(start: Path | None = None) -> list[Check]:
    root = (start or Path.cwd()).expanduser().resolve()
    checks = [
        Check("python", sys.version_info >= (3, 11), sys.version.split()[0]),
        Check("git", shutil.which("git") is not None, shutil.which("git") or "not found"),
        Check("pytest", importlib.util.find_spec("pytest") is not None, "available" if importlib.util.find_spec("pytest") else "not installed"),
        Check("manifest", (root / MANIFEST_NAME).is_file(), str(root / MANIFEST_NAME)),
    ]
    return checks
