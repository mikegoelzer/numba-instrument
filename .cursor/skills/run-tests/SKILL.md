---
name: run-tests
description: Run the hsswitcher pytest suite and capture an agent-readable digest. Use whenever the agent needs to run tests, check pytest results, or verify changes in the hsswitcher Python project.
---

# Run tests

This Python project is called `hsswitcher` and uses a `uv`-managed venv
at `.venv`. Activate it before running any commands.

## Commands

```bash
source .venv/bin/activate
make test && echo "OK"
deactivate
```

If the last line printed is not "OK" then read the output and fix the lint problem(s).

`make test` simply runs pytest in the venv like this:

```bash
pytest --agent-digest=term --agent-digest=file
```

The `--agent-digest=term` flag (provided by `pytest-agent-digest`)
prints a compact summary to the terminal, while `--agent-digest=file` writes a markdown
copy of the output to `reports/pytest-results.md` (configured via
`agent_digest_file` in `pyproject.toml`). Read that file to inspect failures in detail.

## Notes

- If the venv is missing, run `make install-dev` in worktree root first.
- All other pytest flags work as usual; the digest file is overwritten on each run.
