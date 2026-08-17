from __future__ import annotations

from typing import Any


def run(job: dict[str, Any]) -> dict[str, Any]:
    """Execute one bounded OBEOS job."""
    return {"status": "ok", "worker": "{{ project_name }}", "job": job}
