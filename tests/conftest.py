from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.reports import CollectReport, TestReport


def pytest_report_teststatus(
    report: TestReport | CollectReport,
    config: Config,
) -> tuple[str, str, str] | None:
    """Render expected xfails as plain passes in pytest output.

    A test marked ``xfail(strict=True)`` that fails as expected normally shows
    up as ``x`` in the dot output and as ``1 xfailed`` in the summary. We
    intentionally use ``xfail(strict=True)`` to encode "this assertion *must*
    fail under these conditions", which is a passing result for our purposes.
    Strictness still catches the regression case: an unexpected XPASS is
    converted by pytest into a real failure before this hook ever sees it.
    """
    if hasattr(report, "wasxfail") and report.skipped:
        return "passed", ".", "PASSED"
    return None
