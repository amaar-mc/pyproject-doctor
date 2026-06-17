from __future__ import annotations

from pathlib import Path

from pyproject_doctor.checks.dynamic import check_dynamic
from pyproject_doctor.parse import check_file

DATA = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# Unit tests against check_dynamic directly
# ---------------------------------------------------------------------------


def test_static_conflict_version() -> None:
    """version in dynamic AND set statically raises dynamic-static-conflict."""
    data = {"project": {"name": "pkg", "version": "1.0.0", "dynamic": ["version"]}}
    diags = check_dynamic(data)
    assert len(diags) == 1
    assert diags[0].code == "dynamic-static-conflict"
    assert "version" in diags[0].message


def test_name_forbidden() -> None:
    """name in dynamic raises dynamic-name-forbidden."""
    data = {"project": {"name": "pkg", "dynamic": ["name"]}}
    diags = check_dynamic(data)
    assert len(diags) == 1
    assert diags[0].code == "dynamic-name-forbidden"


def test_unknown_field() -> None:
    """Unrecognized field in dynamic raises dynamic-field-unknown."""
    data = {"project": {"name": "pkg", "dynamic": ["not-a-real-field"]}}
    diags = check_dynamic(data)
    assert len(diags) == 1
    assert diags[0].code == "dynamic-field-unknown"
    assert "not-a-real-field" in diags[0].message


def test_valid_dynamic_no_static() -> None:
    """version in dynamic with no static version produces no findings."""
    data = {"project": {"name": "pkg", "dynamic": ["version"]}}
    assert check_dynamic(data) == []


def test_dynamic_absent() -> None:
    """No dynamic field produces no findings."""
    data = {"project": {"name": "pkg", "version": "1.0.0"}}
    assert check_dynamic(data) == []


def test_dynamic_malformed_not_a_list() -> None:
    """dynamic set to a string (not a list) raises dynamic-malformed."""
    data = {"project": {"name": "pkg", "dynamic": "version"}}
    diags = check_dynamic(data)
    assert len(diags) == 1
    assert diags[0].code == "dynamic-malformed"


def test_dynamic_malformed_non_string_entries() -> None:
    """dynamic containing a non-string entry raises dynamic-malformed."""
    data = {"project": {"name": "pkg", "dynamic": [123, "version"]}}
    diags = check_dynamic(data)
    assert len(diags) == 1
    assert diags[0].code == "dynamic-malformed"
    assert diags[0].key_path == "project.dynamic[0]"


def test_multiple_violations_reported() -> None:
    """Both static conflict and name-forbidden are reported when both present."""
    data = {
        "project": {
            "name": "pkg",
            "version": "1.0.0",
            "dynamic": ["name", "version"],
        }
    }
    diags = check_dynamic(data)
    codes = {d.code for d in diags}
    assert "dynamic-name-forbidden" in codes
    assert "dynamic-static-conflict" in codes


def test_no_project_section() -> None:
    """Missing [project] section produces no findings."""
    data: dict[str, object] = {}
    assert check_dynamic(data) == []


def test_all_valid_known_fields() -> None:
    """All recognized PEP 621 field names are accepted without error."""
    from pyproject_doctor.checks.dynamic import _KNOWN_DYNAMIC_FIELDS

    data = {"project": {"name": "pkg", "dynamic": list(_KNOWN_DYNAMIC_FIELDS)}}
    diags = check_dynamic(data)
    unknown = [d for d in diags if d.code == "dynamic-field-unknown"]
    assert unknown == []


# ---------------------------------------------------------------------------
# Fixture-based integration tests (via parse.check_file)
# ---------------------------------------------------------------------------


def test_fixture_static_conflict(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_static_conflict.toml"
    diags = check_file(fixture)
    codes = {d.code for d in diags}
    assert "dynamic-static-conflict" in codes


def test_fixture_name_forbidden(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_name_forbidden.toml"
    diags = check_file(fixture)
    codes = {d.code for d in diags}
    assert "dynamic-name-forbidden" in codes


def test_fixture_field_unknown(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_field_unknown.toml"
    diags = check_file(fixture)
    codes = {d.code for d in diags}
    assert "dynamic-field-unknown" in codes


def test_fixture_valid_dynamic(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_valid.toml"
    diags = check_file(fixture)
    dynamic_errors = [d for d in diags if d.code.startswith("dynamic-")]
    assert dynamic_errors == []


def test_fixture_dynamic_absent(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_absent.toml"
    diags = check_file(fixture)
    dynamic_errors = [d for d in diags if d.code.startswith("dynamic-")]
    assert dynamic_errors == []


def test_fixture_dynamic_malformed(tmp_path: Path) -> None:
    fixture = DATA / "dynamic_malformed.toml"
    diags = check_file(fixture)
    codes = {d.code for d in diags}
    assert "dynamic-malformed" in codes
