from __future__ import annotations


def status() -> dict[str, object]:
    """Return a bounded device status contract."""
    return {
        "status": "ready",
        "device": "{{ project_name }}",
        "capabilities": [],
    }
