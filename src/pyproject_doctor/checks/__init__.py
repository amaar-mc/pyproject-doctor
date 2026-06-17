from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pyproject_doctor.checks.classifiers import check_classifiers
from pyproject_doctor.checks.dependencies import check_dependencies
from pyproject_doctor.checks.dynamic import check_dynamic
from pyproject_doctor.checks.emails import check_emails
from pyproject_doctor.checks.entry_points import check_entry_points
from pyproject_doctor.checks.files import check_files
from pyproject_doctor.checks.urls import check_urls
from pyproject_doctor.checks.version import check_version
from pyproject_doctor.model import Diagnostic


def check_pyproject(data: Mapping[str, Any], *, root: Path) -> list[Diagnostic]:
    """Run all checks on parsed TOML data with root directory for file checks."""
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(check_version(data))
    diagnostics.extend(check_dependencies(data))
    diagnostics.extend(check_files(data, root=root))
    diagnostics.extend(check_urls(data))
    diagnostics.extend(check_emails(data))
    diagnostics.extend(check_entry_points(data))
    diagnostics.extend(check_classifiers(data))
    diagnostics.extend(check_dynamic(data))
    return diagnostics
