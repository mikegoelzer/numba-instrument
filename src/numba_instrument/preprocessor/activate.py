from __future__ import annotations

from collections.abc import Iterable

from .expand import transform_source
from .import_hook import InstrumentingFinder, install_import_instrumentation


def activate(target_modules: Iterable[str]) -> InstrumentingFinder:
    return install_import_instrumentation(target_modules, transform_source)
