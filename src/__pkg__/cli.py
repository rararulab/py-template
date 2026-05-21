"""Typer CLI entry point. Exposed via ``[project.scripts]`` in pyproject.toml."""

from __future__ import annotations

import typer
from rich.console import Console

from __pkg__ import __version__
from __pkg__.core import greet

app = typer.Typer(
    name="__PROJECT_NAME__",
    help="__PROJECT_DESCRIPTION__",
    no_args_is_help=True,
)
console = Console()


@app.command()
def hello(name: str = typer.Argument("world", help="Who to greet.")) -> None:
    """Print a greeting."""
    console.print(greet(name))


@app.command()
def version() -> None:
    """Print the installed package version."""
    console.print(__version__)


if __name__ == "__main__":
    app()
