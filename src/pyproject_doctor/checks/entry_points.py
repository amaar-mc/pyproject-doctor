from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from pyproject_doctor.model import Diagnostic

# Dotted identifier: e.g. "module.submodule" or "module.submodule:attr.sub"
_DOTTED_ID_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$"
)


def _check_ep_ref(ref: str, key_path: str) -> list[Diagnostic]:
    # Strip trailing extras like " [extra1, extra2]"
    ref_stripped = re.sub(r"\s*\[.*\]$", "", ref).strip()
    if ":" not in ref_stripped:
        return [
            Diagnostic(
                level="error",
                code="entry-point-invalid",
                key_path=key_path,
                message=(
                    f"Entry point '{ref}' is missing ':' separator"
                    " (expected 'module:attr' format)"
                ),
            )
        ]
    module_part, attr_part = ref_stripped.split(":", 1)
    errors: list[Diagnostic] = []
    if not _DOTTED_ID_RE.match(module_part):
        errors.append(
            Diagnostic(
                level="error",
                code="entry-point-invalid",
                key_path=key_path,
                message=(
                    f"Entry point '{ref}': module part '{module_part}'"
                    " is not a valid dotted Python identifier"
                ),
            )
        )
    if not _DOTTED_ID_RE.match(attr_part):
        errors.append(
            Diagnostic(
                level="error",
                code="entry-point-invalid",
                key_path=key_path,
                message=(
                    f"Entry point '{ref}': attribute part '{attr_part}'"
                    " is not a valid dotted Python identifier"
                ),
            )
        )
    return errors


def check_entry_points(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check that all entry point references use valid 'module:attr' format."""
    diagnostics: list[Diagnostic] = []
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    for section in ("scripts", "gui-scripts"):
        section_data = project.get(section, {})
        if isinstance(section_data, dict):
            for name, ref in section_data.items():
                if isinstance(ref, str):
                    diagnostics.extend(
                        _check_ep_ref(ref, f"project.{section}.{name}")
                    )

    ep_groups = project.get("entry-points", {})
    if isinstance(ep_groups, dict):
        for group, group_data in ep_groups.items():
            if isinstance(group_data, dict):
                for name, ref in group_data.items():
                    if isinstance(ref, str):
                        diagnostics.extend(
                            _check_ep_ref(
                                ref, f"project.entry-points.{group}.{name}"
                            )
                        )
    return diagnostics
