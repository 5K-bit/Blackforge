import json
from pathlib import Path

import pytest

from blackforge.core.generator import GenerationError, generate_project


@pytest.mark.parametrize(
    ("template_name", "project_name", "expected_files"),
    [
        ("cli", "my-tool", ["README.md", "pyproject.toml", ".gitignore", "tests/test_smoke.py", "my_tool/cli.py"]),
        ("fastapi", "my-api", ["README.md", "pyproject.toml", ".gitignore", "app/main.py", "tests/test_health.py"]),
        ("python-package", "my-package", ["README.md", "pyproject.toml", ".gitignore", "tests/test_package.py", "my_package/__init__.py"]),
        ("obeos-service", "sentinel-bridge", ["README.md", "pyproject.toml", "obeos.manifest.json", "src/sentinel_bridge/main.py", "tests/test_health.py"]),
        ("obeos-agent", "research-agent", ["README.md", "pyproject.toml", "obeos.manifest.json", "src/research_agent/agent.py", "tests/test_agent.py"]),
        ("obeos-skill", "weekly-review", ["README.md", "obeos.manifest.json", "skill.md"]),
        ("obeos-worker", "queue-worker", ["README.md", "pyproject.toml", "obeos.manifest.json", "queue_worker/worker.py"]),
        ("obeos-connector", "telegram-bridge", ["README.md", "pyproject.toml", "obeos.manifest.json", "telegram_bridge/connector.py"]),
        ("obeos-device", "mesh-node", ["README.md", "pyproject.toml", "obeos.manifest.json", "mesh_node/device.py"]),
        ("obeos-event-consumer", "audit-consumer", ["README.md", "pyproject.toml", "obeos.manifest.json", "audit_consumer/consumer.py"]),
        ("obeos-hud", "legion-hud", ["README.md", "pyproject.toml", "obeos.manifest.json", "legion_hud/app.py"]),
    ],
)
def test_generate_project_creates_required_files(
    tmp_path: Path,
    template_name: str,
    project_name: str,
    expected_files: list[str],
) -> None:
    result = generate_project(template_name, project_name, output_dir=tmp_path)
    assert result.destination == (tmp_path / project_name).resolve()
    assert result.destination.is_dir()
    for relative_path in expected_files:
        assert (result.destination / relative_path).exists(), relative_path


def test_generate_project_renders_jinja_variables(tmp_path: Path) -> None:
    result = generate_project("cli", "my-tool", output_dir=tmp_path)
    readme = (result.destination / "README.md").read_text(encoding="utf-8")
    assert "# my-tool" in readme
    assert "Generated with BlackForge on" in readme


def test_obeos_manifest_is_rendered(tmp_path: Path) -> None:
    result = generate_project("obeos-service", "sentinel-bridge", output_dir=tmp_path)
    manifest = json.loads((result.destination / "obeos.manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "sentinel-bridge"
    assert manifest["package"] == "sentinel_bridge"
    assert manifest["component_type"] == "service"
    assert manifest["health"] == "/health"


def test_generate_project_blocks_overwrite_without_force(tmp_path: Path) -> None:
    generate_project("python-package", "my-package", output_dir=tmp_path)
    with pytest.raises(GenerationError):
        generate_project("python-package", "my-package", output_dir=tmp_path)


def test_generate_project_allows_overwrite_with_force(tmp_path: Path) -> None:
    result = generate_project("python-package", "my-package", output_dir=tmp_path)
    package_init = result.destination / "my_package/__init__.py"
    package_init.write_text("changed", encoding="utf-8")
    generate_project("python-package", "my-package", output_dir=tmp_path, force=True)
    assert '"""my-package package."""' in package_init.read_text(encoding="utf-8")


def test_generate_project_preview_does_not_write(tmp_path: Path) -> None:
    result = generate_project("obeos-worker", "preview-worker", output_dir=tmp_path, preview=True)
    assert result.preview is True
    assert result.created_files
    assert not result.destination.exists()


@pytest.mark.parametrize("project_name", ["../escape", "nested/project", "nested\\project", ".."])
def test_generate_project_rejects_unsafe_project_names(tmp_path: Path, project_name: str) -> None:
    with pytest.raises(GenerationError):
        generate_project("cli", project_name, output_dir=tmp_path)
