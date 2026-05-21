"""Typer CLI entry point. Exposed via ``[project.scripts]`` in pyproject.toml."""

from __future__ import annotations

from typing import Annotated

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


# typer ≥0.13 added an overload whose default value carries ``ParamType[Unknown]``,
# tripping pyright's reportUnknownMemberType. Suppression is the workaround until
# typer ships fully-typed stubs (track astral-sh/typer#XXX).
@app.command()
def hello(
    name: Annotated[str, typer.Argument(help="Who to greet.")] = "world",  # pyright: ignore[reportUnknownMemberType]
) -> None:
    """Print a greeting."""
    console.print(greet(name))


@app.command()
def version() -> None:
    """Print the installed package version."""
    console.print(__version__)


if __name__ == "__main__":
    app()
