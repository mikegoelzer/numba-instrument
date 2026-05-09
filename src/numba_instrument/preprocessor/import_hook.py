from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import sys
import types
from collections.abc import Callable, Iterable, Sequence

SourceTransform = Callable[[str, str, str], str]


class InstrumentingLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname: str, path: str, transform: SourceTransform):
        """
        Capture the transform function we were instantiated with for later use.

        Args:
            fullname: The full name of the module.
            path: The path to the module.
            transform: The transform function to apply to the module source.
        """
        super().__init__(fullname, path)
        self._transform = transform

    # Linter ignore: We narrow the base signature (StrPath | ReadableBuffer | ast.*) 
    # since we only get invoked by our own SourceLoader.get_code, which always 
    # passes path as a str and data as bytes.
    def source_to_code(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: bytes, path: str, *, _optimize: int = -1
    ) -> types.CodeType:
        # Not all modules use utf-8, so let importlib decide how to decode.
        source = importlib.util.decode_source(data)

        # Invoke the transform we were instantiated with.
        transformed = self._transform(source, path, self.name)

        # Compile the transformed source into a CodeType object.
        return compile(
            transformed, 
            path, 
            "exec", 
            dont_inherit=True, 
            optimize=_optimize,
        )

    # Linter ignore: wide base signature not needed since this func is a no-op for us.
    def set_data(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, path: str, data: bytes, *, _mode: int = 0o666
    ) -> None:
        """
        Do not write the bytecode cache since we do custom transform at import time
        (this only applies to the few modules we handle).
        """
        return None

    def get_code(self, fullname: str) -> types.CodeType:
        """
        Do not read the bytecode cache for same reason as in set_data.

        SourceLoader.get_code would happily reuse a stale bytecode file that predates 
        (or doesn't reflect) our transform, so source_to_code would never run and 
        the module would import un-instrumented.

        (Removing this function should cause `test_import_hook.py` to fail to catch 
        the regression.)
        """
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
    """Insert the InstrumentingFinder at the front of sys.meta_path.

    Args:
        target_modules: The modules to instrument.
        transform: The transform function to apply to the module source.

    Returns:
        The InstrumentingFinder instance.
    """
    finder = InstrumentingFinder(target_modules, transform)
    sys.meta_path.insert(0, finder)
    return finder
