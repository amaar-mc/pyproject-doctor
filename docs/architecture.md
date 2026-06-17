# Architecture

## Overview

pyproject-doctor is organized into a thin CLI shell over a pure-function core.

```
pyproject.toml file
       |
   parse.py (check_file)
       |
   tomllib / tomli
       |
   Mapping[str, Any]
       |
  checks/__init__.py (check_pyproject)
       |
  +----+----+----+----+----+----+----+
  |    |    |    |    |    |    |    |
 ver  dep  file url email  ep  cls
```

Each check is an independent pure function that takes `Mapping[str, Any]` (and optionally a `root: Path`) and returns `list[Diagnostic]`.

## Diagnostic Model

`Diagnostic` is a frozen dataclass with:
- `level`: "error" | "warning" | "info"
- `code`: stable kebab-case identifier (e.g., "version-invalid")
- `key_path`: dotted location in the TOML (e.g., "project.dependencies[0]")
- `message`: human-readable explanation

## Checks

### version (checks/version.py)

Uses `packaging.version.Version` to validate PEP 440. Skips if "version" is in `project.dynamic`.

### dependencies (checks/dependencies.py)

Uses `packaging.requirements.Requirement` to validate PEP 508. Also runs satisfiability analysis.

### Constraint Satisfiability Algorithm

The satisfiability checker analyzes the specifiers in a `SpecifierSet` to detect impossible version ranges.

**Algorithm:**

1. Parse all specifiers from the set.
2. Track an effective lower bound `(version, inclusive: bool)` and upper bound `(version, inclusive: bool)`.
3. For each specifier operator:
   - `==X`: adds X as both lower and upper bound (inclusive). Multiple different `==` pins are immediately unsatisfiable.
   - `>=X`: update lower bound to max(current_lower, X) with inclusive=True.
   - `>X`: update lower bound to max(current_lower, X) with inclusive=False (exclusive is tighter at same version).
   - `<=X`: update upper bound to min(current_upper, X) with inclusive=True.
   - `<X`: update upper bound to min(current_upper, X) with inclusive=False.
   - `~=X.Y`: treated as `>=X.Y` for lower bound purposes.
   - `!=X`: never contributes to unsatisfiability alone; excluded from analysis.
   - `==X.*` (wildcard): skipped (too complex to bound tightly).
4. After processing all specifiers, check:
   - If `lower_ver > upper_ver`: unsatisfiable.
   - If `lower_ver == upper_ver` and either endpoint is exclusive: unsatisfiable.
   - Otherwise: satisfiable.

**Examples:**
- `>=2.0,<1.0`: lower=2.0(inc), upper=1.0(exc) => 2.0 > 1.0 => unsatisfiable
- `>1.0,<=1.0`: lower=1.0(exc), upper=1.0(inc) => equal bounds, lower exclusive => unsatisfiable
- `>=1.0,<=1.0`: lower=1.0(inc), upper=1.0(inc) => equal bounds, both inclusive => satisfiable (exactly 1.0)
- `!=1.0,!=2.0`: no bounds derived => satisfiable

### files (checks/files.py)

Checks `project.readme`, `project.license.file`, `project.license-files` globs, and entry-point module paths. File checks are relative to the `root` directory. Entry-point module checks only run when `src/` exists under root, to avoid false positives on installed packages.

### urls (checks/urls.py)

Uses `urllib.parse.urlparse` to validate that each `project.urls` value has both a scheme and a netloc.

### emails (checks/emails.py)

Uses a pragmatic regex pattern to validate author/maintainer email addresses.

### entry_points (checks/entry_points.py)

Validates that each entry-point reference is in `module:attr` format, where both module and attr are valid dotted Python identifiers.

### classifiers (checks/classifiers.py)

Imports `trove_classifiers` at runtime. If not installed, emits an info diagnostic and skips. If installed, validates each classifier string against the known set.
