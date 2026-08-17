from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from blackforge.core.doctor import run_doctor
from blackforge.core.generator import GenerationError, generate_project
from blackforge.core.manifest import inspect_component, validate_manifest
from blackforge.core.templates import list_templates
from blackforge.ui.console import console, error, info, success

app = typer.Typer(help="BlackForge: local-first OBEOS development toolchain.")
new_app = typer.Typer(help="Create a new project from a template.")
app.add_typer(new_app, name="new")


@app.command("list-templates")
def list_templates_command() -> None:
    """List all available built-in templates."""
    available = list_templates()
    if not available:
        info("No templates found.")
        return

    table = Table(title="Available Templates")
    table.add_column("Template", style="magenta")
    for template_name in available:
        table.add_row(template_name)
    console.print(table)


def _create(template_name: str, project_name: str, force: bool, preview: bool) -> None:
    try:
        result = generate_project(
            template_name=template_name,
            project_name=project_name,
            output_dir=Path.cwd(),
            force=force,
            preview=preview,
        )
    except (GenerationError, ValueError) as exc:
        error(str(exc))
        raise typer.Exit(code=1) from exc

    action = "Previewed" if result.preview else "Created"
    success(
        f"{action} '{result.project_name}' from template '{template_name}' "
        f"at {result.destination}"
    )
    info(f"{'Would generate' if result.preview else 'Generated'} {len(result.created_files)} files.")


@app.command("create")
def create_from_template(
    template_name: str,
    project_name: str,
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite destination if it exists.")] = False,
    preview: Annotated[bool, typer.Option("--preview", help="Show generation plan without writing files.")] = False,
) -> None:
    """Create a project from any installed BlackForge template."""
    _create(template_name, project_name, force, preview)


@app.command("inspect")
def inspect_command(path: Path = Path.cwd()) -> None:
    """Inspect the nearest OBEOS component manifest."""
    try:
        report = inspect_component(path)
    except FileNotFoundError as exc:
        error(str(exc))
        raise typer.Exit(code=1) from exc

    table = Table(title=f"OBEOS Component: {report.data.get('name', 'unknown')}")
    table.add_column("Field")
    table.add_column("Value")
    for key in ("component", "version", "entrypoint", "schema_version"):
        table.add_row(key, str(report.data.get(key, "")))
    console.print(table)
    if report.warnings:
        for warning in report.warnings:
            info(f"Warning: {warning}")
    if not report.valid:
        for message in report.errors:
            error(message)
        raise typer.Exit(code=1)
    success(f"Manifest valid: {report.path}")


@app.command("validate")
def validate_command(path: Path = Path("obeos.manifest.json")) -> None:
    """Validate an OBEOS component manifest."""
    if not path.is_file():
        error(f"Manifest not found: {path}")
        raise typer.Exit(code=1)
    report = validate_manifest(path.resolve())
    for warning in report.warnings:
        info(f"Warning: {warning}")
    if report.errors:
        for message in report.errors:
            error(message)
        raise typer.Exit(code=1)
    success(f"Valid OBEOS manifest: {report.path}")


@app.command("doctor")
def doctor_command(path: Path = Path.cwd()) -> None:
    """Check whether the current environment is ready for BlackForge/OBEOS development."""
    table = Table(title="BlackForge Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    failed = False
    for check in run_doctor(path):
        table.add_row(check.name, "OK" if check.ok else "FAIL", check.detail)
        failed = failed or not check.ok
    console.print(table)
    if failed:
        raise typer.Exit(code=1)
    success("Environment ready.")


def _project_command(template_name: str):
    def command(
        project_name: str,
        force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite destination if it exists.")] = False,
        preview: Annotated[bool, typer.Option("--preview", help="Show generation plan without writing files.")] = False,
    ) -> None:
        _create(template_name, project_name, force, preview)

    return command


for _template in (
    "cli",
    "fastapi",
    "python-package",
    "obeos-agent",
    "obeos-connector",
    "obeos-device",
    "obeos-event-consumer",
    "obeos-hud",
    "obeos-service",
    "obeos-skill",
    "obeos-worker",
):
    new_app.command(_template)(_project_command(_template))


if __name__ == "__main__":
    app()
