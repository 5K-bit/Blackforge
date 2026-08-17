from __future__ import annotations

from typing import Any


def connect(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Establish the connector boundary without hiding transport state."""
    return {"status": "ready", "connector": "{{ project_name }}", "config": config or {}}
