"""Library entry points.

Keep CLI-side concerns (argument parsing, terminal rendering) out of this
module so the package can be imported and exercised from tests or other
libraries without dragging in click/typer/rich.
"""

from __future__ import annotations


def greet(name: str) -> str:
    """Return a friendly greeting for ``name``.

    Args:
        name: The name to greet. Must be non-empty.

    Returns:
        A greeting like ``"Hello, world!"``.

    Raises:
        ValueError: If ``name`` is empty after stripping whitespace.
    """
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must be non-empty")
    return f"Hello, {cleaned}!"
