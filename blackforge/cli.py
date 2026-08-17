from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from blackforge.core.generator import GenerationError, generate_project
from blackforge.core.templates import list_templates
from blackforge.ui.console import console, error, info, success

app = typer.Typer(help="BlackForge: local-first project scaffolding for OBEOS and general Python development.")
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


def _create(template_name: str, project_name: str, force: bool) -> None:
    try:
        result = generate_project(
            template_name=template_name,
            project_name=project_name,
            output_dir=Path.cwd(),
            force=force,
        )
    except (GenerationError, ValueError) as exc:
        error(str(exc))
        raise typer.Exit(code=1) from exc

    success(
        f"Created '{result.project_name}' from template '{template_name}' "
        f"at {result.destination}"
    )
    info(f"Generated {len(result.created_files)} files.")


@app.command("create")
def create_from_template(
    template_name: str,
    project_name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Overwrite destination if it exists.")
    ] = False,
) -> None:
    """Create a project from any installed BlackForge template."""
    _create(template_name, project_name, force)


def _project_command(template_name: str):
    def command(
        project_name: str,
        force: Annotated[
            bool,
            typer.Option("--force", "-f", help="Overwrite destination if it exists."),
        ] = False,
    ) -> None:
        _create(template_name, project_name, force)

    return command


new_app.command("cli")(_project_command("cli"))
new_app.command("fastapi")(_project_command("fastapi"))
new_app.command("python-package")(_project_command("python-package"))
new_app.command("obeos-service")(_project_command("obeos-service"))
new_app.command("obeos-agent")(_project_command("obeos-agent"))
new_app.command("obeos-skill")(_project_command("obeos-skill"))


if __name__ == "__main__":
    app()
