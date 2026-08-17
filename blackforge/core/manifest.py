from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MANIFEST_NAME = "obeos.manifest.json"
REQUIRED_FIELDS = {"schema_version", "name", "version", "entrypoint"}
ALLOWED_COMPONENTS = {
    "agent",
    "connector",
    "device",
    "event-consumer",
    "hud",
    "service",
    "skill",
    "worker",
}


@dataclass(slots=True)
class ManifestReport:
    path: Path
    data: dict[str, Any]
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def component_type(self) -> str | None:
        value = self.data.get("component_type") or self.data.get("component")
        return value if isinstance(value, str) else None


def find_manifest(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).expanduser().resolve()
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        candidate = directory / MANIFEST_NAME
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Could not find {MANIFEST_NAME} from {current}")


def validate_manifest(path: Path) -> ManifestReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ManifestReport(path, {}, [f"Invalid JSON: {exc}"], [])

    if not isinstance(data, dict):
        return ManifestReport(path, {}, ["Manifest root must be a JSON object."], [])

    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    component = data.get("component_type") or data.get("component")
    if component is None:
        errors.append("Missing required field: component_type")
    elif not isinstance(component, str):
        errors.append("component_type must be a string.")
    elif component not in ALLOWED_COMPONENTS:
        errors.append(
            f"Unsupported component_type '{component}'. Expected one of: "
            f"{', '.join(sorted(ALLOWED_COMPONENTS))}"
        )

    if "component" in data and "component_type" not in data:
        warnings.append("Legacy field 'component' detected; use 'component_type' for new manifests.")

    entrypoint = data.get("entrypoint")
    if entrypoint and not isinstance(entrypoint, str):
        errors.append("entrypoint must be a string.")

    interfaces = data.get("interfaces", [])
    if not isinstance(interfaces, list):
        errors.append("interfaces must be a list when present.")

    if data.get("schema_version") != 1:
        warnings.append("Unknown schema_version; BlackForge currently targets schema version 1.")

    return ManifestReport(path, data, errors, warnings)


def inspect_component(start: Path | None = None) -> ManifestReport:
    return validate_manifest(find_manifest(start))
