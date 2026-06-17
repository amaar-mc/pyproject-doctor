# pyproject-doctor Charter

## Mission

pyproject-doctor catches semantic mistakes in pyproject.toml that other validators miss. It runs fully offline, with no network calls, and produces structured diagnostics that are easy to consume in CI or pre-commit hooks.

## Scope

pyproject-doctor validates:

- PEP 440 version strings
- PEP 508 dependency specifiers
- Version constraint satisfiability
- File existence (readme, license, entry-point modules)
- URL format in project.urls
- Email format in authors/maintainers
- Entry-point format (module:attr)
- Trove classifier validity (optional)

pyproject-doctor does NOT:
- Validate build backends beyond requiring valid PEP 508 in build-system.requires
- Import or execute any project code
- Make network calls
- Replace a full build system

## Stability

Diagnostic codes (e.g., version-invalid, dep-invalid) are stable and will not change without a major version bump.
