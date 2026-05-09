from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import cast

import pytest

from numba_instrument.preprocessor.import_hook import (
    InstrumentingFinder,
    install_import_instrumentation,
)

FIXTURES_DIR = Path(__file__).parent / "test_fixtures"
FIXTURE_MODULE = "sample_module"


def test_finder_tracks_exact_target_modules() -> None:
    finder = InstrumentingFinder(
        ["example.target"],
        lambda source, filename, module_name: source,
    )

    assert "example.target" in finder.target_modules
    assert "example.other" not in finder.target_modules


@pytest.mark.parametrize(
    "do_install",
    [
        True,
        pytest.param(
            False,
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "With do_install=False the InstrumentingFinder is never inserted "
                    "into sys.meta_path, so sample_module loads via the default "
                    "Python loader without our transform. INSTRUMENTED is therefore "
                    "absent and the `is True` assertion must fail. Marked strict so "
                    "Suite breaks loudly if do_install=False ever passes (which would "
                    "indicate a hook leaking across tests or fixture contamination)."
                ),
            ),
        ),
    ],
)
def test_loader_imports_local_module_and_applies_transform(do_install: bool) -> None:
    """End-to-end import test, parametrized over whether the hook is installed.

    The transform appends ``INSTRUMENTED = True`` to the source of
    ``sample_module``. The test then imports the module from disk and asserts
    that ``module.INSTRUMENTED is True``.

    - ``do_install=True``: ``install_import_instrumentation`` runs, the
      InstrumentingLoader compiles the transformed source, and the assertion
      passes -- proving the loader successfully loads a real on-disk module
      *and* routes its source through our transform.
    - ``do_install=False``: the install step is skipped, so the module loads
      via Python's default SourceFileLoader without the transform. The
      ``INSTRUMENTED`` attribute is missing and the same assertion fails. This
      branch is wrapped in ``pytest.mark.xfail(strict=True)`` so the expected
      failure keeps the suite green, while a surprise pass (e.g. a stale hook
      leaking from another test) is reported as a hard failure.
    """

    captured: dict[str, str] = {}

    def transform(source: str, filename: str, module_name: str) -> str:
        """Perform text-based transform on imported module source."""
        captured["filename"] = filename
        captured["module_name"] = module_name
        return source + "\nINSTRUMENTED = True\n"

    fixtures_path = str(FIXTURES_DIR)
    sys.path.insert(0, fixtures_path)
    sys.modules.pop(FIXTURE_MODULE, None)
    finder: InstrumentingFinder | None = None
    if do_install:
        finder = install_import_instrumentation([FIXTURE_MODULE], transform)
    try:
        module = importlib.import_module(FIXTURE_MODULE)

        assert cast(str, module.GREETING) == "hello"
        assert cast(int, module.add(2, 3)) == 5
        assert cast(bool, getattr(module, "INSTRUMENTED", False)) is True

        module_file = cast(str, module.__file__)
        expected = (FIXTURES_DIR / f"{FIXTURE_MODULE}.py").resolve()
        assert Path(module_file).resolve() == expected
        assert captured["module_name"] == FIXTURE_MODULE
        assert Path(captured["filename"]).resolve() == expected
    finally:
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)
        sys.modules.pop(FIXTURE_MODULE, None)
        if fixtures_path in sys.path:
            sys.path.remove(fixtures_path)
