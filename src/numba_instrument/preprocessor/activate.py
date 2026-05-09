from __future__ import annotations

from collections.abc import Iterable

from .import_hook import InstrumentingFinder, install_import_instrumentation
from .transform_code import transform_source


def activate(target_modules: Iterable[str]) -> InstrumentingFinder:
    return install_import_instrumentation(target_modules, transform=transform_source)
