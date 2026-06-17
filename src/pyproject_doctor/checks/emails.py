from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from pyproject_doctor.model import Diagnostic

# Pragmatic email pattern: local@domain.tld
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)


def _check_email(email: str, key_path: str) -> list[Diagnostic]:
    if not _EMAIL_RE.match(email):
        return [
            Diagnostic(
                level="error",
                code="email-invalid",
                key_path=key_path,
                message=f"'{email}' does not look like a valid email address",
            )
        ]
    return []


def _check_person_list(
    people: list[Any], section: str
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for i, person in enumerate(people):
        if not isinstance(person, dict):
            continue
        email = person.get("email")
        if isinstance(email, str):
            diagnostics.extend(
                _check_email(email, f"project.{section}[{i}].email")
            )
    return diagnostics


def check_emails(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check author and maintainer email fields."""
    diagnostics: list[Diagnostic] = []
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    for section in ("authors", "maintainers"):
        people = project.get(section, [])
        if isinstance(people, list):
            diagnostics.extend(_check_person_list(people, section))

    return diagnostics
