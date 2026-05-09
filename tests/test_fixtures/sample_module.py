"""Fixture module loaded via the instrumenting import hook in tests."""

from __future__ import annotations

GREETING = "hello"


def add(a: int, b: int) -> int:
    return a + b
