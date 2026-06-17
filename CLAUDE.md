# CLAUDE.md

## Project: pyproject-doctor

Offline deep validator for pyproject.toml. Catches semantic mistakes other tools miss.

## Key Design Decisions

- Pure functions for all checks; CLI and file IO are thin shells.
- No default parameter values anywhere; expose named variants if needed.
- Strict mypy typing throughout.
- `packaging` library for PEP 440 and PEP 508 validation only.
- Optional `trove-classifiers` for classifier validation; gracefully skip if absent.
- Satisfiability checker is custom (packaging has no is_satisfiable).
- File existence checks only run when `src/` exists under root.

## Adding Checks

1. Add a pure function to `src/pyproject_doctor/checks/<module>.py`.
2. Compose it in `src/pyproject_doctor/checks/__init__.py`.
3. Write tests first.
4. Stable diagnostic codes are kebab-case; never rename them.

## Gates Before Committing

```
uv pip install -e ".[dev]"
uv run pytest -q
uv run ruff check .
uv run mypy src
uv build
uv run --with twine twine check dist/*
```
