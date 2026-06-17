# pyproject-doctor

<p align="center">
  <img src="assets/logo.png" alt="pyproject-doctor logo" width="160">
</p>

Offline deep validator for `pyproject.toml` that catches the semantic mistakes other tools miss.

Most validators only check TOML syntax. pyproject-doctor goes further: it validates that your versions are PEP 440 compliant, your dependencies are PEP 508 compliant, your version constraints are actually satisfiable, your referenced files exist, your URLs are real URLs, your email addresses look right, and your entry-point references are correctly formatted.

> **PyPI release pending.** Install from GitHub for now (see below).

## What it checks

| Code | Description |
|------|-------------|
| `version-invalid` | `project.version` is not a valid PEP 440 version |
| `dep-invalid` | A dependency in `project.dependencies`, `project.optional-dependencies`, or `build-system.requires` is not a valid PEP 508 requirement |
| `constraint-unsatisfiable` | A dependency's version specifiers form an impossible range (e.g. `>=2.0,<1.0`) |
| `file-missing` | A file referenced by `project.readme`, `project.license`, or an entry-point module does not exist |
| `url-invalid` | A value in `project.urls` is not a valid absolute URL |
| `email-invalid` | An author or maintainer email address is malformed |
| `entry-point-invalid` | A script or entry-point value is not in valid `module:attr` format |
| `classifier-unknown` | A classifier in `project.classifiers` is not a known trove classifier (requires `pip install 'pyproject-doctor[classifiers]'`) |

## Install

```bash
pip install git+https://github.com/amaar-mc/pyproject-doctor.git
```

Or with classifier validation:

```bash
pip install "git+https://github.com/amaar-mc/pyproject-doctor.git#egg=pyproject-doctor[classifiers]"
```

## Usage

```bash
# Validate pyproject.toml in the current directory
pyproject-doctor

# Validate a specific file
pyproject-doctor /path/to/pyproject.toml

# JSON output
pyproject-doctor --format json
```

Exit code is 1 if any error-level diagnostic is found, 0 otherwise.

## Pre-commit

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/amaar-mc/pyproject-doctor
    rev: v0.1.0
    hooks:
      - id: pyproject-doctor
```

## Example output

```
error project.version: version-invalid: 'not.a.version' is not a valid PEP 440 version
error project.dependencies[0]: constraint-unsatisfiable: Dependency 'requests': constraint '>=3.0,<2.0' is unsatisfiable (lower bound 3.0 exceeds upper bound 2.0)
error project.urls.Homepage: url-invalid: URL 'not-a-url' is not a valid absolute URL (must have scheme and host)
```

## License

MIT. Copyright (c) 2026 Amaar Chughtai.
