from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pyproject_doctor.model import Diagnostic


def check_classifiers(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check that project.classifiers are known trove classifiers."""
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []
    classifiers = project.get("classifiers", [])
    if not isinstance(classifiers, list):
        return []
    if not classifiers:
        return []

    try:
        import trove_classifiers  # type: ignore[import-not-found,unused-ignore]
        known: set[str] = trove_classifiers.classifiers
    except ImportError:
        return [
            Diagnostic(
                level="info",
                code="classifiers-skipped",
                key_path="project.classifiers",
                message=(
                    "trove-classifiers is not installed; classifier validation"
                    " skipped. Install with: pip install 'pyproject-doctor[classifiers]'"
                ),
            )
        ]

    diagnostics: list[Diagnostic] = []
    for i, classifier in enumerate(classifiers):
        if not isinstance(classifier, str):
            continue
        if classifier not in known:
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="classifier-unknown",
                    key_path=f"project.classifiers[{i}]",
                    message=f"Unknown classifier: '{classifier}'",
                )
            )
    return diagnostics
