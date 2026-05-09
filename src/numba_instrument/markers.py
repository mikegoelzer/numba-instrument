from __future__ import annotations

try:
    from numba import njit
except Exception:  # pragma: no cover
    njit = None  # type: ignore[assignment]


if njit is not None:
    @njit(inline="always")
    def __instrumentation_probe__(_unused):  # type: ignore[no-untyped-def]
        return None
else:
    def __instrumentation_probe__(_unused):  # type: ignore[no-untyped-def]
        return None
