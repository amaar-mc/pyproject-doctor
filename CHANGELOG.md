# Changelog

All notable changes to pyproject-doctor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-06-23

### Added

- PEP 639 SPDX license-expression validation. New diagnostic code
  `license-expression-invalid`: validates `project.license` when it is given in
  the modern string form (for example `license = "MIT"`,
  `license = "MIT OR Apache-2.0"`, or `license = "Apache-2.0 WITH LLVM-exception"`).
  It validates the SPDX expression grammar (license identifiers, `WITH` exception
  clauses, `AND` / `OR` operators, and parentheses) against a vendored, curated set
  of common SPDX license and exception identifiers, with no new runtime dependency.
  It flags an empty expression, an unknown license or exception identifier, a
  deprecated identifier (suggesting the canonical replacement), the PEP-639
  disallowed `+` suffix (recommending the `-or-later` form), a misplaced operator,
  and unbalanced parentheses. The legacy table form
  (`{ file = "..." }` / `{ text = "..." }`) is intentionally not treated as an
  expression, and an absent license field produces no finding.

## [0.3.0] - 2026-06-21

### Added

- `requires-python` validity check. New diagnostic code `requires-python-invalid`:
  flags a `project.requires-python` value that is not a string, is empty, is not a
  valid PEP 440 version specifier set, or specifies an unsatisfiable range (for
  example `>=3.12,<3.8`). A valid value or an absent `requires-python` produces no finding.
- SARIF 2.1.0 output format for the CLI: `pyproject-doctor --format sarif`. Each
  diagnostic maps to one SARIF result, the diagnostic code becomes the `ruleId`,
  and the SARIF level (error, warning, note) is derived from the diagnostic level.
  The pure renderer lives in `pyproject_doctor.sarif.to_sarif`.

## [0.2.0] - 2026-06-17

### Added

- PEP 621 `dynamic` field correctness check. Four new diagnostic codes:
  - `dynamic-malformed`: `project.dynamic` is not a list of strings.
  - `dynamic-name-forbidden`: `name` is listed in `project.dynamic` (PEP 621 forbids this).
  - `dynamic-field-unknown`: an entry in `project.dynamic` is not a recognized `[project]` field name.
  - `dynamic-static-conflict`: a field listed in `project.dynamic` is also set statically in `[project]`.

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

[0.3.0]: https://github.com/amaar-mc/pyproject-doctor/releases/tag/v0.3.0
[0.2.0]: https://github.com/amaar-mc/pyproject-doctor/releases/tag/v0.2.0
[0.1.0]: https://github.com/amaar-mc/pyproject-doctor/releases/tag/v0.1.0
