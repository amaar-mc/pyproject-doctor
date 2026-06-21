from __future__ import annotations

from pathlib import Path

from pyproject_doctor.checks.requires_python import check_requires_python
from pyproject_doctor.parse import check_file

DATA = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# Unit tests against check_requires_python directly
# ---------------------------------------------------------------------------


def test_valid_specifier_no_finding() -> None:
    data = {"project": {"name": "pkg", "requires-python": ">=3.10,<4.0"}}
    assert check_requires_python(data) == []


def test_simple_valid_specifier_no_finding() -> None:
    data = {"project": {"name": "pkg", "requires-python": ">=3.8"}}
    assert check_requires_python(data) == []


def test_absent_no_finding() -> None:
    data = {"project": {"name": "pkg", "version": "1.0.0"}}
    assert check_requires_python(data) == []


def test_no_project_section_no_finding() -> None:
    data: dict[str, object] = {}
    assert check_requires_python(data) == []


def test_invalid_specifier() -> None:
    data = {"project": {"name": "pkg", "requires-python": "not a specifier"}}
    diags = check_requires_python(data)
    assert len(diags) == 1
    assert diags[0].code == "requires-python-invalid"
    assert diags[0].key_path == "project.requires-python"
    assert diags[0].level == "error"


def test_empty_specifier() -> None:
    data = {"project": {"name": "pkg", "requires-python": "   "}}
    diags = check_requires_python(data)
    assert len(diags) == 1
    assert diags[0].code == "requires-python-invalid"
    assert "empty" in diags[0].message


def test_non_string_specifier() -> None:
    data = {"project": {"name": "pkg", "requires-python": 3.10}}
    diags = check_requires_python(data)
    assert len(diags) == 1
    assert diags[0].code == "requires-python-invalid"
    assert "string" in diags[0].message


def test_unsatisfiable_specifier() -> None:
    data = {"project": {"name": "pkg", "requires-python": ">=3.12,<3.8"}}
    diags = check_requires_python(data)
    assert len(diags) == 1
    assert diags[0].code == "requires-python-invalid"
    assert "unsatisfiable" in diags[0].message


def test_exclusive_bounds_at_same_version_unsatisfiable() -> None:
    data = {"project": {"name": "pkg", "requires-python": ">3.10,<3.10"}}
    diags = check_requires_python(data)
    assert len(diags) == 1
    assert diags[0].code == "requires-python-invalid"


def test_dynamic_requires_python_skipped() -> None:
    data = {"project": {"name": "pkg", "dynamic": ["requires-python"]}}
    assert check_requires_python(data) == []


# ---------------------------------------------------------------------------
# Fixture-based integration tests (via parse.check_file)
# ---------------------------------------------------------------------------


def test_fixture_invalid() -> None:
    diags = check_file(DATA / "requires_python_invalid.toml")
    codes = {d.code for d in diags}
    assert "requires-python-invalid" in codes


def test_fixture_unsatisfiable() -> None:
    diags = check_file(DATA / "requires_python_unsatisfiable.toml")
    codes = {d.code for d in diags}
    assert "requires-python-invalid" in codes


def test_fixture_valid() -> None:
    diags = check_file(DATA / "requires_python_valid.toml")
    rp_errors = [d for d in diags if d.code == "requires-python-invalid"]
    assert rp_errors == []


def test_fixture_absent() -> None:
    diags = check_file(DATA / "requires_python_absent.toml")
    rp_errors = [d for d in diags if d.code == "requires-python-invalid"]
    assert rp_errors == []


def test_clean_fixture_has_no_requires_python_finding() -> None:
    diags = check_file(DATA / "clean.toml")
    rp_errors = [d for d in diags if d.code == "requires-python-invalid"]
    assert rp_errors == []
