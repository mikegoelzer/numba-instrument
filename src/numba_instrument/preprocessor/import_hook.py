from __future__ import annotations

import ast
import importlib.abc
import importlib.machinery
import sys
import types
from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import ReadableBuffer, StrPath

SourceTransform = Callable[[str, str, str], str]


class InstrumentingLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname: str, path: str, transform: SourceTransform):
        super().__init__(fullname, path)
        self._transform = transform

    def source_to_code(
        self,
        data: ReadableBuffer | str | types.ModuleType | ast.Expression | ast.Interactive,
        path: StrPath,
        *,
        _optimize: int = -1,
    ) -> types.CodeType:
        if isinstance(data, str):
            source = data
        elif isinstance(data, (bytes, bytearray, memoryview)):
            source = bytes(data).decode("utf-8")
        else:
            return super().source_to_code(data, path, _optimize=_optimize)
        path_str = path.decode("utf-8") if isinstance(path, bytes) else str(path)
        transformed = self._transform(source, path_str, self.name)
        return compile(transformed, path_str, "exec", dont_inherit=True, optimize=_optimize)

    def set_data(
        self,
        path: StrPath,
        data: ReadableBuffer,
        *,
        _mode: int = 0o666,
    ) -> None:
        # Avoid writing transformed bytecode caches.
        return None


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
