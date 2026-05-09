.PHONY: all
all:
	@echo "run 'make install' to install the package"
	@echo "run 'make install-dev' to install the package with development dependencies"
	@echo "run 'make clean' to remove all temporary artifacts including the venv, numba and __pycache__"
	@echo "run 'make test' to run all tests (quick first, then slow if no failures)"
	@echo "run 'make linters' to run ruff, basedpyright, radon and xenon"

.PHONY: clean-numba
clean-numba:
	@find . -type d -name __pycache__ -print0 \
		| xargs -0 -I{} find {} -type f \( -name '*.nbi' -o -name '*.nbc' \) -delete
	@echo "Numba cache flushed."

.PHONY: clean
clean: clean-numba
	@rm -rf .venv
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

.PHONY: test
test:
	@pytest -q ; \
	exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

.PHONY: linters
linters:
	@# ruff: run the lint checks defined in [tool.ruff] / [tool.ruff.lint] in
	@# pyproject.toml (rule selection, line-length, mccabe + pylint limits,
	@# target-version, src layout). Ruff auto-discovers the nearest
	@# pyproject.toml, so the only argument we need is the path to scan.
	@#   check  -> run the linter (as opposed to the formatter)
	@#   src tests -> walk both first-party trees declared in [tool.ruff].src
	uv run ruff check src tests
	@exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

	@# basedpyright: type-check using [tool.basedpyright] from pyproject.toml.
	@# That section already pins the venv (venvPath/venv), pythonVersion,
	@# typeCheckingMode, and every reportXxx severity, and lists the paths to
	@# include, so basedpyright needs no CLI flags.
	uv run basedpyright
	@exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

	@# radon cc: cyclomatic-complexity report. Radon >= 6.0 reads
	@# [tool.radon] from pyproject.toml automatically (cc_min, show_complexity,
	@# total_average, exclude). We only pass the path to scan; tests are
	@# excluded via pyproject.toml.
	uv run radon cc src
	@exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

	@# radon mi: maintainability-index report. Same [tool.radon] section is
	@# applied (show_mi -> --show, exclude). Path-only invocation again.
	uv run radon mi src
	@exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

	@# xenon: hard-fail when complexity exceeds a threshold. Xenon does NOT
	@# read pyproject.toml, so the limits are passed on the CLI to mirror
	@# radon's cc_min = "B".
	@#   --max-absolute B  no single block worse than CC grade B (= 6..10)
	@#   --max-modules  B  no per-module average worse than B
	@#   --max-average  A  project-wide average must stay at A (CC <= 5)
	uv run xenon --max-absolute B --max-modules B --max-average A src
	@exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		exit $$exit_code; \
	fi

.PHONY: build
build:
	@rm -rf dist build
	@uv build --sdist --wheel

.PHONY: install
install:
	@uv python pin 3.12
	@uv sync --no-dev

.PHONY: install-dev
install-dev: 
	@uv python pin 3.12
	@uv sync --all-extras --dev --link-mode=copy
	@echo ""
	@echo "To activate the environment, run:"
	@echo "  source .venv/bin/activate"
