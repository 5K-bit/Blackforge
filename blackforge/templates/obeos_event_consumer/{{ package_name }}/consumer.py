from __future__ import annotations

from typing import Any


def handle(event: dict[str, Any]) -> dict[str, Any]:
    """Consume one bounded OBEOS event."""
    return {"status": "processed", "consumer": "{{ project_name }}", "event": event}
