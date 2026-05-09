from __future__ import annotations

from numba_instrument.preprocessor.import_hook import InstrumentingFinder


def test_finder_tracks_exact_target_modules() -> None:
    finder = InstrumentingFinder(
        ["example.target"],
        lambda source, filename, module_name: source,
    )

    assert "example.target" in finder.target_modules
    assert "example.other" not in finder.target_modules
