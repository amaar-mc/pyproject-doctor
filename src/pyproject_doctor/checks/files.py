from __future__ import annotations

import glob
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pyproject_doctor.model import Diagnostic


def _check_file_exists(file_path: str, key_path: str, root: Path) -> list[Diagnostic]:
    full = root / file_path
    if not full.exists():
        return [
            Diagnostic(
                level="error",
                code="file-missing",
                key_path=key_path,
                message=f"Referenced file '{file_path}' does not exist under {root}",
            )
        ]
    return []


def _check_readme(project: dict[str, Any], root: Path) -> list[Diagnostic]:
    readme = project.get("readme")
    if readme is None:
        return []
    if isinstance(readme, str):
        return _check_file_exists(readme, "project.readme", root)
    if isinstance(readme, dict):
        file_val = readme.get("file")
        if isinstance(file_val, str):
            return _check_file_exists(file_val, "project.readme.file", root)
    return []


def _check_license(project: dict[str, Any], root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    license_val = project.get("license")
    if isinstance(license_val, dict):
        file_val = license_val.get("file")
        if isinstance(file_val, str):
            diagnostics.extend(
                _check_file_exists(file_val, "project.license.file", root)
            )
    # PEP 639 license-files (list of globs)
    license_files = project.get("license-files")
    if isinstance(license_files, list):
        for i, pattern in enumerate(license_files):
            if isinstance(pattern, str):
                matches = glob.glob(str(root / pattern))
                if not matches:
                    diagnostics.append(
                        Diagnostic(
                            level="error",
                            code="file-missing",
                            key_path=f"project.license-files[{i}]",
                            message=f"license-files glob '{pattern}' matches no files under {root}",
                        )
                    )
    return diagnostics


def _is_valid_dotted_identifier(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$", s))


def _check_entry_point_file(
    ref: str, key_path: str, root: Path
) -> list[Diagnostic]:
    """Check if the module part of a module:attr entry point exists as a file."""
    # Strip extras like "module:attr [extra]"
    ref_stripped = ref.split("[")[0].strip()
    if ":" not in ref_stripped:
        return []
    module_part = ref_stripped.split(":")[0].strip()
    if not _is_valid_dotted_identifier(module_part):
        return []

    top_module = module_part.split(".")[0]

    # Only report missing if we can find a src/ directory (so we don't false-positive
    # on installed packages)
    src_dir = root / "src"
    if not src_dir.exists():
        return []

    # Check if top-level module exists anywhere under src/
    top_candidates = [
        root / "src" / (top_module + ".py"),
        root / "src" / top_module / "__init__.py",
    ]
    if not any(c.exists() for c in top_candidates):
        return [
            Diagnostic(
                level="warning",
                code="file-missing",
                key_path=key_path,
                message=(
                    f"Entry point module '{module_part}' not found under"
                    f" {root / 'src'} (checked {[str(c) for c in top_candidates]})"
                ),
            )
        ]
    return []


def _check_entry_points_files(data: Mapping[str, Any], root: Path) -> list[Diagnostic]:
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
                        _check_entry_point_file(
                            ref, f"project.{section}.{name}", root
                        )
                    )

    ep_groups = project.get("entry-points", {})
    if isinstance(ep_groups, dict):
        for group, group_data in ep_groups.items():
            if isinstance(group_data, dict):
                for name, ref in group_data.items():
                    if isinstance(ref, str):
                        diagnostics.extend(
                            _check_entry_point_file(
                                ref,
                                f"project.entry-points.{group}.{name}",
                                root,
                            )
                        )
    return diagnostics


def check_files(data: Mapping[str, Any], *, root: Path) -> list[Diagnostic]:
    """Check file existence for readme, license, and entry-point module paths."""
    diagnostics: list[Diagnostic] = []
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    diagnostics.extend(_check_readme(project, root))
    diagnostics.extend(_check_license(project, root))
    diagnostics.extend(_check_entry_points_files(data, root))
    return diagnostics
