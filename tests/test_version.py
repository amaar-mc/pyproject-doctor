from __future__ import annotations

import pytest

from pyproject_doctor.checks.version import check_version


def test_valid_version() -> None:
    data = {"project": {"version": "1.2.3"}}
    assert check_version(data) == []


def test_invalid_version() -> None:
    data = {"project": {"version": "not-a-version"}}
    diags = check_version(data)
    assert len(diags) == 1
    assert diags[0].code == "version-invalid"


def test_dynamic_version_skipped() -> None:
    data = {"project": {"dynamic": ["version"]}}
    assert check_version(data) == []


def test_missing_version_ok() -> None:
    data = {"project": {"name": "foo"}}
    assert check_version(data) == []


def test_non_string_version() -> None:
    data = {"project": {"version": 123}}
    diags = check_version(data)
    assert len(diags) == 1
    assert diags[0].code == "version-invalid"


@pytest.mark.parametrize("version", [
    "0.1.0",
    "1.0.0a1",
    "1.0.0.post1",
    "1.0.0.dev1",
    "2023.01.01",
])
def test_valid_version_forms(version: str) -> None:
    data = {"project": {"version": version}}
    assert check_version(data) == []
