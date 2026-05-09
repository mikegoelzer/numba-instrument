"""Fixture module loaded via the instrumenting import hook in tests."""

from __future__ import annotations

from numba import njit

GREETING = "hello"

@njit
def add(a: int, b: int) -> int:
    return a + b
