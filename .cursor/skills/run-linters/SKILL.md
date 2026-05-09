---
name: run-tests
description: Run the hsswitcher linters suite to verify all code is of adequate quality. Use whenever the agent needs to run tests or verify changes in the hsswitcher Python project.
---

# Run linters

This Python project is called `hsswitcher` and uses a `uv`-managed venv
at `.venv`. Activate it before running any commands.

## Commands

```bash
source .venv/bin/activate
make linters && "OK"
deactivate
```

If the last line printed is not "OK" then read the output and fix the lint problem(s).

## Notes

- If the venv is missing, run `make install-dev` in worktree root first.
- Quick subset: `pytest -m "not slow"` (or `make test-quick`).
- All other pytest flags work as usual; the digest file is overwritten on each run.
