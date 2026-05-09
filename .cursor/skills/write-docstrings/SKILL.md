---
name: write-docstrings
description: Write concise Google-style docstrings for Python functions and methods in hsswitcher. Use whenever the agent creates a new function, or adds a missing docstring to an existing function it is modifying.
---

# Write docstrings

This project requires a docstring on every non-trivial function or method.
Docstrings are short, machine-readable contracts; they are not narrative.

## Format

- Use triple-double-quoted strings (`"""..."""`) placed on the line
  immediately after the `def` line.
- First line: a single, present-tense imperative sentence describing
  what the function does. No trailing period if it fits on one line as a
  one-line docstring. Add a period when followed by a blank line and
  more sections.
- For functions that take arguments or return a meaningful value, add
  `Arguments:` and `Returns:` sections (Google style). Keep entries to
  one line each whenever possible.
- Omit the section header for a category that does not apply (e.g. a
  procedure with no return value omits `Returns:`).
- Type information already lives in the type annotations; do not repeat
  types inside the docstring.

## One-line form

For functions whose contract is fully captured by a single sentence and
whose arguments are self-describing, a one-line docstring is enough:

```python
def slugify(value: str) -> str:
    """Lowercase `value` and replace non-alnum runs with single hyphens."""
    ...
```

## Multi-line form

When a function takes arguments worth describing or returns a non-obvious
value, expand to the full form:

```python
def resolve_pid_path(value: str, *, temp_dir: Path) -> Path:
    """Resolve a configured PID file string to an absolute path.

    Arguments:
        value: Raw `pid_file` value from config; either an absolute path,
            a `~`-prefixed path, or a bare filename.
        temp_dir: Directory used as the base when `value` is not absolute.

    Returns:
        Fully expanded, absolute `Path` (no `~`, no relative segments).
    """
    ...
```

## When to skip a docstring

A function is "trivial" and may be left undocumented when **all** of the
following hold:

- Its body is one line (or a single `return` statement).
- Its name + parameter names + return type already convey its contract.
- It has no side effects worth flagging.

Concretely, the following are typically trivial:

- Pass-through getters/setters: `def host(self) -> str: return self._host`.
- Dunder methods that delegate to `super()` with no extra logic.
- One-line `@property` accessors of a single field.
- Pydantic / dataclass field definitions (the field metadata is the doc).

When in doubt, write the docstring.

## Modifying existing functions

- If the function has **no docstring**, add one that follows this skill.
- If the function **already has a docstring**, do **not** rewrite it,
  even if it does not match this style. The only exception is when the
  function's contract (signature, behavior, return shape) genuinely
  changed in this edit; in that case update the relevant lines minimally
  and preserve the rest verbatim.

## Examples

### Good

```python
def kill_previous(pid_file: Path) -> bool:
    """Kill the process recorded in `pid_file` if it is still alive.

    Arguments:
        pid_file: Path to a single-line file containing the previous
            instance's PID. Missing or unreadable files are treated as
            "no previous instance".

    Returns:
        True if a process was signalled, False otherwise.
    """
    ...
```

```python
def _is_loopback(host: str) -> bool:
    """Return True if `host` resolves to a loopback interface."""
    ...
```

### Bad

```python
def kill_previous(pid_file: Path) -> bool:
    """
    This function kills the previous process.

    :param pid_file: a Path object pointing to a file containing a PID
        as a string. The PID is read from the file as text and parsed
        into an int. If the file does not exist, no action is taken.
    :type pid_file: Path
    :returns: a boolean
    :rtype: bool
    """
    ...
```

Why it's bad: Sphinx-style sections instead of Google; redundant types
duplicated from the annotations; padded prose instead of a one-line
contract; describes the implementation rather than the behavior.

## Quick checklist

- [ ] Triple-double-quoted, placed under the `def` line.
- [ ] Single-line summary in imperative mood.
- [ ] `Arguments:` section present when the function takes arguments
      whose role is not obvious from the name + type.
- [ ] `Returns:` section present when the function returns a meaningful
      value.
- [ ] No types repeated from the annotations.
- [ ] Existing docstrings on functions you are editing are left alone.
