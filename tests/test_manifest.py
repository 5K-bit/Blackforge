import json
from pathlib import Path

from blackforge.core.generator import generate_project
from blackforge.core.manifest import find_manifest, validate_manifest


def test_validate_generated_obeos_manifest(tmp_path: Path) -> None:
    result = generate_project("obeos-agent", "planner", output_dir=tmp_path)
    report = validate_manifest(result.destination / "obeos.manifest.json")
    assert report.valid
    assert report.component_type == "agent"


def test_find_manifest_walks_up_parent_directories(tmp_path: Path) -> None:
    result = generate_project("obeos-service", "api", output_dir=tmp_path)
    nested = result.destination / "nested" / "deeper"
    nested.mkdir(parents=True)
    assert find_manifest(nested) == result.destination / "obeos.manifest.json"


def test_validate_manifest_rejects_unknown_component(tmp_path: Path) -> None:
    path = tmp_path / "obeos.manifest.json"
    path.write_text(
        json.dumps({
            "schema_version": 1,
            "name": "bad",
            "component_type": "mystery",
            "version": "0.1.0",
            "entrypoint": "bad:main",
        }),
        encoding="utf-8",
    )
    report = validate_manifest(path)
    assert not report.valid
    assert any("Unsupported component_type" in error for error in report.errors)
