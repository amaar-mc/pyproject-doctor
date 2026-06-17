from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from pyproject_doctor.model import Diagnostic


def _is_wildcard(version_str: str) -> bool:
    return "*" in version_str


def _update_lower(
    current: tuple[Version, bool] | None, candidate_ver: Version, inclusive: bool
) -> tuple[Version, bool]:
    """Return the tighter (higher) lower bound."""
    if current is None:
        return (candidate_ver, inclusive)
    cur_ver, cur_inc = current
    if candidate_ver > cur_ver:
        return (candidate_ver, inclusive)
    if candidate_ver == cur_ver and cur_inc and not inclusive:
        # exclusive is tighter than inclusive at same version
        return (candidate_ver, inclusive)
    return current


def _update_upper(
    current: tuple[Version, bool] | None, candidate_ver: Version, inclusive: bool
) -> tuple[Version, bool]:
    """Return the tighter (lower) upper bound."""
    if current is None:
        return (candidate_ver, inclusive)
    cur_ver, cur_inc = current
    if candidate_ver < cur_ver:
        return (candidate_ver, inclusive)
    if candidate_ver == cur_ver and cur_inc and not inclusive:
        # exclusive is tighter than inclusive at same version
        return (candidate_ver, inclusive)
    return current


def _check_satisfiability(
    specifier_str: str, key_path: str, dep_name: str
) -> list[Diagnostic]:
    """Check if a specifier set is satisfiable by analyzing version bounds."""
    try:
        ss = SpecifierSet(specifier_str)
    except Exception:
        return []

    specifiers = list(ss)
    if not specifiers:
        return []

    lower_bound: tuple[Version, bool] | None = None
    upper_bound: tuple[Version, bool] | None = None
    exact_pins: list[Version] = []

    for spec in specifiers:
        op = spec.operator
        version_str = spec.version

        if _is_wildcard(version_str):
            continue

        ver = Version(version_str)

        if op == "==":
            exact_pins.append(ver)
            lower_bound = _update_lower(lower_bound, ver, True)
            upper_bound = _update_upper(upper_bound, ver, True)
        elif op == "!=":
            pass
        elif op == ">=":
            lower_bound = _update_lower(lower_bound, ver, True)
        elif op == ">":
            lower_bound = _update_lower(lower_bound, ver, False)
        elif op == "<=":
            upper_bound = _update_upper(upper_bound, ver, True)
        elif op == "<":
            upper_bound = _update_upper(upper_bound, ver, False)
        elif op == "~=":
            lower_bound = _update_lower(lower_bound, ver, True)

    # Multiple conflicting exact pins
    if len(exact_pins) > 1:
        unique_pins = {str(p) for p in exact_pins}
        if len(unique_pins) > 1:
            return [
                Diagnostic(
                    level="error",
                    code="constraint-unsatisfiable",
                    key_path=key_path,
                    message=(
                        f"Dependency '{dep_name}': conflicting exact pins"
                        f" '{specifier_str}' cannot satisfy multiple different"
                        f" == constraints simultaneously"
                    ),
                )
            ]

    if lower_bound is not None and upper_bound is not None:
        lb_ver, lb_inclusive = lower_bound
        ub_ver, ub_inclusive = upper_bound

        if lb_ver > ub_ver:
            return [
                Diagnostic(
                    level="error",
                    code="constraint-unsatisfiable",
                    key_path=key_path,
                    message=(
                        f"Dependency '{dep_name}': constraint '{specifier_str}'"
                        f" is unsatisfiable (lower bound {lb_ver} exceeds"
                        f" upper bound {ub_ver})"
                    ),
                )
            ]
        if lb_ver == ub_ver and not (lb_inclusive and ub_inclusive):
            return [
                Diagnostic(
                    level="error",
                    code="constraint-unsatisfiable",
                    key_path=key_path,
                    message=(
                        f"Dependency '{dep_name}': constraint '{specifier_str}'"
                        f" is unsatisfiable (exclusive bounds at same version"
                        f" {lb_ver})"
                    ),
                )
            ]

    return []


def check_requirement(req_str: str, key_path: str) -> list[Diagnostic]:
    """Check a single PEP 508 requirement string for validity and satisfiability."""
    try:
        req = Requirement(req_str)
    except InvalidRequirement as e:
        return [
            Diagnostic(
                level="error",
                code="dep-invalid",
                key_path=key_path,
                message=f"'{req_str}' is not a valid PEP 508 requirement: {e}",
            )
        ]

    diagnostics: list[Diagnostic] = []
    if req.specifier:
        diagnostics.extend(
            _check_satisfiability(str(req.specifier), key_path, req.name)
        )
    return diagnostics


def check_dependencies(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check all dependency fields for PEP 508 validity and constraint satisfiability."""
    diagnostics: list[Diagnostic] = []
    project = data.get("project", {})

    if isinstance(project, dict):
        deps = project.get("dependencies", [])
        if isinstance(deps, list):
            for i, dep in enumerate(deps):
                if isinstance(dep, str):
                    diagnostics.extend(
                        check_requirement(dep, f"project.dependencies[{i}]")
                    )

        opt_deps = project.get("optional-dependencies", {})
        if isinstance(opt_deps, dict):
            for group, group_deps in opt_deps.items():
                if isinstance(group_deps, list):
                    for i, dep in enumerate(group_deps):
                        if isinstance(dep, str):
                            diagnostics.extend(
                                check_requirement(
                                    dep,
                                    f"project.optional-dependencies.{group}[{i}]",
                                )
                            )

    build_system = data.get("build-system", {})
    if isinstance(build_system, dict):
        requires = build_system.get("requires", [])
        if isinstance(requires, list):
            for i, dep in enumerate(requires):
                if isinstance(dep, str):
                    diagnostics.extend(
                        check_requirement(dep, f"build-system.requires[{i}]")
                    )

    return diagnostics
