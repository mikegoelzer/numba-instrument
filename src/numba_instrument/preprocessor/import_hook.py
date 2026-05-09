from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
import types
from collections.abc import Callable, Iterable, Sequence

SourceTransform = Callable[[str, str, str], str]


class InstrumentingLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname: str, path: str, transform: SourceTransform):
        super().__init__(fullname, path)
        self._transform = transform

    # Ignore note: SourceLoader.get_code always invokes source_to_code with the bytes
    # returns from get_data() and the str path returned by get_filename(), so we narrow
    # base signature (StrPath | ReadableBuffer | ast.*) to what actually flows in.
    def source_to_code(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes, path: str, *, _optimize: int = -1
    ) -> types.CodeType:
        source = data.decode("utf-8")
        transformed = self._transform(source, path, self.name)
        return compile(transformed, path, "exec", dont_inherit=True, optimize=_optimize)

    # Ignore note: we never write bytecode caches, so wide base signature not needed.
    def set_data(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, path: str, data: bytes, *, _mode: int = 0o666
    ) -> None:
        return None

    # Bypass the .pyc cache: SourceLoader.get_code would happily reuse a stale
    # bytecode file that predates (or doesn't reflect) our transform, so
    # source_to_code would never run and the module would import un-instrumented.
    def get_code(self, fullname: str) -> types.CodeType:
        source_path = self.get_filename(fullname)
        source_bytes = self.get_data(source_path)
        return self.source_to_code(source_bytes, source_path)


class InstrumentingFinder(importlib.abc.MetaPathFinder):
    def __init__(self, target_modules: Iterable[str], transform: SourceTransform):
        self.target_modules = set(target_modules)
        self.transform = transform

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname not in self.target_modules:
            return None

        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None:
            return None

        if not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            return None

        if spec.origin is None or not spec.origin.endswith(".py"):
            return None

        spec.loader = InstrumentingLoader(fullname, spec.origin, self.transform)
        return spec


def install_import_instrumentation(
    target_modules: Iterable[str],
    transform: SourceTransform,
) -> InstrumentingFinder:
    finder = InstrumentingFinder(target_modules, transform)
    sys.meta_path.insert(0, finder)
    return finder
