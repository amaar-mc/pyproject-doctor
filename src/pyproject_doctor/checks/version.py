from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from packaging.version import InvalidVersion, Version

from pyproject_doctor.model import Diagnostic


def check_version(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check that project.version is a valid PEP 440 version."""
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []
    dynamic = project.get("dynamic", [])
    if isinstance(dynamic, list) and "version" in dynamic:
        return []
    version = project.get("version")
    if version is None:
        return []
    if not isinstance(version, str):
        return [
            Diagnostic(
                level="error",
                code="version-invalid",
                key_path="project.version",
                message=f"version must be a string, got {type(version).__name__}",
            )
        ]
    try:
        Version(version)
    except InvalidVersion:
        return [
            Diagnostic(
                level="error",
                code="version-invalid",
                key_path="project.version",
                message=f"'{version}' is not a valid PEP 440 version",
            )
        ]
    return []
