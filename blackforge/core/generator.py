from datetime import datetime, timezone
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader

from blackforge.core.result import GenerationResult
from blackforge.core.templates import get_templates_dir, resolve_template_name


class GenerationError(Exception):
    """Raised when project generation cannot proceed."""


def _to_package_name(project_name: str) -> str:
    package = re.sub(r"[^a-zA-Z0-9]+", "_", project_name).strip("_").lower()
    if not package:
        raise GenerationError("Project name must contain letters or numbers.")
    return package


def generate_project(
    template_name: str,
    project_name: str,
    output_dir: Path | None = None,
    force: bool = False,
) -> GenerationResult:
    destination_root = output_dir or Path.cwd()
    destination = destination_root / project_name
    template_key = resolve_template_name(template_name)
    template_dir = get_templates_dir() / template_key

    if destination.exists() and not force:
        raise GenerationError(
            f"Destination '{destination}' already exists. Use --force to overwrite."
        )

    destination.mkdir(parents=True, exist_ok=True)

    context = {
        "project_name": project_name,
        "package_name": _to_package_name(project_name),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    }

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
        autoescape=False,
    )

    created_files: list[Path] = []
    for source in sorted(template_dir.rglob("*")):
        relative_path = source.relative_to(template_dir).as_posix()
        rendered_relative = env.from_string(relative_path).render(**context)
        target = destination / rendered_relative

        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        rendered_content = env.get_template(relative_path).render(**context)
        target.write_text(rendered_content, encoding="utf-8")
        created_files.append(target.relative_to(destination))

    return GenerationResult(
        template_name=template_name,
        project_name=project_name,
        destination=destination,
        created_files=created_files,
    )
