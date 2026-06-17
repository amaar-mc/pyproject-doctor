from __future__ import annotations

import pytest

from pyproject_doctor.checks.entry_points import check_entry_points


@pytest.mark.parametrize("ref", [
    "module:function",
    "module.submodule:function",
    "my_pkg.cli:main",
    "pkg:func [extra]",
])
def test_valid_entry_points(ref: str) -> None:
    data = {"project": {"scripts": {"my-cmd": ref}}}
    assert check_entry_points(data) == []


@pytest.mark.parametrize("ref", [
    "no_colon",
    "123module:func",
    "module:123attr",
    ":func",
    "module:",
])
def test_invalid_entry_points(ref: str) -> None:
    data = {"project": {"scripts": {"my-cmd": ref}}}
    diags = check_entry_points(data)
    assert any(d.code == "entry-point-invalid" for d in diags)
