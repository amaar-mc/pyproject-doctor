from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from pyproject_doctor.model import Diagnostic


def _is_wildcard(version_str: str) -> bool:
    return "*" in version_str


def _is_unsatisfiable(specifier_set: SpecifierSet) -> bool:
    """Return True when the specifier set admits no possible version.

    Analyzes the lower and upper bounds the way the dependency satisfiability
    checker does, but scoped to requires-python so it carries its own diagnostic.
    """
    lower_ver: Version | None = None
    lower_inclusive = True
    upper_ver: Version | None = None
    upper_inclusive = True

    for spec in specifier_set:
        version_str = spec.version
        if _is_wildcard(version_str):
            continue
        ver = Version(version_str)
        op = spec.operator
        if op in ("==", ">=", "~="):
            if lower_ver is None or ver > lower_ver:
                lower_ver, lower_inclusive = ver, True
        elif op == ">":
            if lower_ver is None or ver > lower_ver or (ver == lower_ver and lower_inclusive):
                lower_ver, lower_inclusive = ver, False
        if op in ("==", "<="):
            if upper_ver is None or ver < upper_ver:
                upper_ver, upper_inclusive = ver, True
        elif op == "<":
            if upper_ver is None or ver < upper_ver or (ver == upper_ver and upper_inclusive):
                upper_ver, upper_inclusive = ver, False

    if lower_ver is not None and upper_ver is not None:
        if lower_ver > upper_ver:
            return True
        if lower_ver == upper_ver and not (lower_inclusive and upper_inclusive):
            return True
    return False


def check_requires_python(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check that project.requires-python is a valid, satisfiable PEP 440 specifier set.

    Flags `requires-python-invalid` when the value is not a string, is empty or
    whitespace, is not a valid PEP 440 version specifier set, or specifies an
    unsatisfiable range (for example `>=3.12,<3.8`). A clean value or an absent
    requires-python produces no finding.
    """
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    dynamic = project.get("dynamic", [])
    if isinstance(dynamic, list) and "requires-python" in dynamic:
        return []

    value = project.get("requires-python")
    if value is None:
        return []

    if not isinstance(value, str):
        return [
            Diagnostic(
                level="error",
                code="requires-python-invalid",
                key_path="project.requires-python",
                message=(
                    f"requires-python must be a string, got {type(value).__name__}"
                ),
            )
        ]

    if value.strip() == "":
        return [
            Diagnostic(
                level="error",
                code="requires-python-invalid",
                key_path="project.requires-python",
                message="requires-python is empty; expected a PEP 440 version specifier set",
            )
        ]

    try:
        specifier_set = SpecifierSet(value)
    except InvalidSpecifier as e:
        return [
            Diagnostic(
                level="error",
                code="requires-python-invalid",
                key_path="project.requires-python",
                message=(
                    f"'{value}' is not a valid PEP 440 version specifier set: {e}"
                ),
            )
        ]

    if _is_unsatisfiable(specifier_set):
        return [
            Diagnostic(
                level="error",
                code="requires-python-invalid",
                key_path="project.requires-python",
                message=(
                    f"requires-python '{value}' is unsatisfiable;"
                    f" no Python version can satisfy it"
                ),
            )
        ]

    return []
