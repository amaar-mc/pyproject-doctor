# Contributing to pyproject-doctor

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository.
2. Install in editable mode with dev dependencies:

```bash
uv pip install -e ".[dev]"
```

3. Run tests:

```bash
uv run pytest -q
```

4. Run linting:

```bash
uv run ruff check .
uv run mypy src
```

## Adding a New Check

1. Write a failing test first (`tests/test_<check>.py`).
2. Add a pure function to the appropriate module under `src/pyproject_doctor/checks/`.
3. Expose it via `check_pyproject` in `src/pyproject_doctor/checks/__init__.py`.
4. Add test data files to `tests/data/` as needed.
5. Update `docs/architecture.md` to describe the check.
6. Update `CHANGELOG.md` under `[Unreleased]`.

## Commit Style

Commits use the `type(scope): description` format. For example:

- `feat(checks): add Python version compatibility check`
- `fix(deps): handle wildcard specifiers in satisfiability check`
- `test(version): add test for post-release versions`

## Code Style

- Strict mypy typing required.
- No default parameter values.
- Pure functions for checks.
- No em dashes in code, comments, or docs.
