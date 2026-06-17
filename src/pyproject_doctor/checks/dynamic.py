from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pyproject_doctor.model import Diagnostic

# PEP 621 recognized [project] field names that may appear in dynamic
_KNOWN_DYNAMIC_FIELDS: frozenset[str] = frozenset(
    {
        "version",
        "description",
        "readme",
        "requires-python",
        "license",
        "authors",
        "maintainers",
        "keywords",
        "classifiers",
        "urls",
        "scripts",
        "gui-scripts",
        "entry-points",
        "dependencies",
        "optional-dependencies",
    }
)


def check_dynamic(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check PEP 621 dynamic field correctness.

    Rules enforced:
    - dynamic must be a list of strings (dynamic-malformed).
    - 'name' must not appear in dynamic (dynamic-name-forbidden).
    - Every entry must be a recognized [project] field name (dynamic-field-unknown).
    - A field listed in dynamic must not also be set statically in [project]
      (dynamic-static-conflict).
    """
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    raw_dynamic = project.get("dynamic")
    if raw_dynamic is None:
        return []

    diagnostics: list[Diagnostic] = []

    if not isinstance(raw_dynamic, list):
        diagnostics.append(
            Diagnostic(
                level="error",
                code="dynamic-malformed",
                key_path="project.dynamic",
                message=(
                    f"project.dynamic must be a list of strings,"
                    f" got {type(raw_dynamic).__name__}"
                ),
            )
        )
        return diagnostics

    for i, entry in enumerate(raw_dynamic):
        if not isinstance(entry, str):
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="dynamic-malformed",
                    key_path=f"project.dynamic[{i}]",
                    message=(
                        f"project.dynamic entries must be strings,"
                        f" got {type(entry).__name__} at index {i}"
                    ),
                )
            )

    # Collect only the valid string entries for further checks
    string_entries: list[tuple[int, str]] = [
        (i, entry) for i, entry in enumerate(raw_dynamic) if isinstance(entry, str)
    ]

    for i, field in string_entries:
        if field == "name":
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="dynamic-name-forbidden",
                    key_path=f"project.dynamic[{i}]",
                    message=(
                        "'name' must not be listed in project.dynamic;"
                        " the project name is always required to be static (PEP 621)"
                    ),
                )
            )
            continue

        if field not in _KNOWN_DYNAMIC_FIELDS:
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="dynamic-field-unknown",
                    key_path=f"project.dynamic[{i}]",
                    message=(
                        f"'{field}' is not a recognized [project] field name"
                        f" for project.dynamic (PEP 621)"
                    ),
                )
            )
            continue

        if field in project:
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="dynamic-static-conflict",
                    key_path=f"project.dynamic[{i}]",
                    message=(
                        f"'{field}' is listed in project.dynamic but is also"
                        f" set statically in [project]; a field may not be both"
                        f" dynamic and static (PEP 621)"
                    ),
                )
            )

    return diagnostics
