from __future__ import annotations

import pytest

from pyproject_doctor.checks.dependencies import (
    _check_satisfiability,
    check_dependencies,
    check_requirement,
)


@pytest.mark.parametrize("req", [
    "requests",
    "requests>=2.28",
    "requests>=2.0,<3.0",
    "requests==2.28.0",
    "flask[async]>=2.0",
    "tomli>=2.0; python_version < '3.11'",
    "numpy>=1.20,<2.0",
])
def test_valid_requirements(req: str) -> None:
    assert check_requirement(req, "project.dependencies[0]") == []


@pytest.mark.parametrize("req", [
    "not a valid requirement!!!",
    ">=2.0",  # Missing name
])
def test_invalid_requirements(req: str) -> None:
    diags = check_requirement(req, "project.dependencies[0]")
    assert any(d.code == "dep-invalid" for d in diags)


# Satisfiability tests
@pytest.mark.parametrize("specifier", [
    ">=1.0,<2.0",
    ">=1.0,<=2.0",
    ">=1.0",
    "<2.0",
    "==1.0.0",
    ">=1.0,!=1.5",
    "~=1.4",
    ">=1.0,<2.0,!=1.5",
    ">=1.0,<1.1",
    ">=1.0,<=1.0",  # satisfiable: exactly 1.0
])
def test_satisfiable_specifiers(specifier: str) -> None:
    diags = _check_satisfiability(specifier, "project.dependencies[0]", "foo")
    assert diags == [], f"Expected satisfiable but got: {diags}"


@pytest.mark.parametrize("specifier", [
    ">=2.0,<1.0",
    ">2.0,<=1.0",
    ">=2.0,<=1.0",
    ">1.0,<1.0",
    ">=1.0,<1.0",  # exclusive upper == lower bound
    ">1.0,<=1.0",  # exclusive lower == upper bound
    "==1.0,==2.0",  # two different exact pins
    ">=3.0,<2.0",
])
def test_unsatisfiable_specifiers(specifier: str) -> None:
    diags = _check_satisfiability(specifier, "project.dependencies[0]", "foo")
    assert any(d.code == "constraint-unsatisfiable" for d in diags), \
        f"Expected unsatisfiable but got no diagnostic for: {specifier}"


def test_check_dependencies_full() -> None:
    data = {
        "project": {
            "dependencies": ["requests>=2.0,<1.0"],
        }
    }
    diags = check_dependencies(data)
    assert any(d.code == "constraint-unsatisfiable" for d in diags)


def test_ne_alone_not_unsatisfiable() -> None:
    diags = _check_satisfiability("!=1.0,!=2.0,!=3.0", "p.d[0]", "foo")
    assert diags == []
