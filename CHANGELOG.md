# Changelog

All notable changes to pyproject-doctor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-17

### Added

- PEP 621 `dynamic` field correctness check. Four new diagnostic codes:
  - `dynamic-malformed`: `project.dynamic` is not a list of strings.
  - `dynamic-name-forbidden`: `name` is listed in `project.dynamic` (PEP 621 forbids this).
  - `dynamic-field-unknown`: an entry in `project.dynamic` is not a recognized `[project]` field name.
  - `dynamic-static-conflict`: a field listed in `project.dynamic` is also set statically in `[project]`.

### Notes

- PyPI publish is queued behind the new-project quota (429). Install from GitHub or build from source.

## [0.1.0] - 2026-06-17

### Added

- Initial release of pyproject-doctor.
- PEP 440 version validation (`version-invalid`).
- PEP 508 dependency validation (`dep-invalid`) for `project.dependencies`, `project.optional-dependencies`, and `build-system.requires`.
- Version constraint satisfiability checking (`constraint-unsatisfiable`): detects impossible version ranges.
- File existence validation (`file-missing`) for readme, license, and entry-point module paths.
- URL format validation (`url-invalid`) for `project.urls`.
- Email format validation (`email-invalid`) for authors and maintainers.
- Entry-point format validation (`entry-point-invalid`) for scripts, gui-scripts, and entry-points.
- Trove classifier validation (`classifier-unknown`) via optional `trove-classifiers` dependency.
- Text and JSON output formats.
- Pre-commit hook support via `.pre-commit-hooks.yaml`.
- CLI: `pyproject-doctor [PATH] [--format text|json]`.

### Notes

- PyPI release is pending. Install from source or GitHub for now.

[0.1.0]: https://github.com/amaar-mc/pyproject-doctor/releases/tag/v0.1.0
