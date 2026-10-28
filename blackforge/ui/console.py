from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"info": "#ffb36b", "success": "green", "error": "bold red"}))


def info(message: str) -> None:
    console.print(f"[info]{message}[/info]")


def success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def error(message: str) -> None:
    console.print(f"[bold red]{message}[/bold red]")
