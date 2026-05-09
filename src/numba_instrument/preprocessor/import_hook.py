from __future__ import annotations

import importlib.abc
import importlib.machinery
import sys
from collections.abc import Callable, Iterable


SourceTransform = Callable[[str, str, str], str]


class InstrumentingLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname: str, path: str, transform: SourceTransform):
        super().__init__(fullname, path)
        self._transform = transform

    def source_to_code(self, data: bytes | str, path: str, *, _optimize: int = -1):
        source = data.decode("utf-8") if isinstance(data, bytes) else data
        transformed = self._transform(source, path, self.name)
        return compile(transformed, path, "exec", dont_inherit=True, optimize=_optimize)

    def set_data(self, path: str, data: bytes) -> None:
        # Avoid writing transformed bytecode caches.
        return None


class InstrumentingFinder(importlib.abc.MetaPathFinder):
    def __init__(self, target_modules: Iterable[str], transform: SourceTransform):
        self.target_modules = set(target_modules)
        self.transform = transform

    def find_spec(self, fullname: str, path=None, target=None):
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
