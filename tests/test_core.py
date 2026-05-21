"""Tests for __pkg__.core."""

from __future__ import annotations

import pytest

from __pkg__.core import greet


def test_greet_returns_greeting() -> None:
    assert greet("world") == "Hello, world!"


def test_greet_strips_whitespace() -> None:
    assert greet("  Alice  ") == "Hello, Alice!"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_greet_rejects_empty(bad: str) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        greet(bad)
