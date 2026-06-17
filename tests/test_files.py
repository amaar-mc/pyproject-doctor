from __future__ import annotations

from pathlib import Path

from pyproject_doctor.checks.files import check_files


def test_readme_string_exists(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Hello")
    data = {"project": {"readme": "README.md"}}
    assert check_files(data, root=tmp_path) == []


def test_readme_string_missing(tmp_path: Path) -> None:
    data = {"project": {"readme": "README.md"}}
    diags = check_files(data, root=tmp_path)
    assert any(d.code == "file-missing" for d in diags)


def test_readme_table_exists(tmp_path: Path) -> None:
    (tmp_path / "README.rst").write_text("Hello")
    data = {"project": {"readme": {"file": "README.rst", "content-type": "text/x-rst"}}}
    assert check_files(data, root=tmp_path) == []


def test_license_file_exists(tmp_path: Path) -> None:
    (tmp_path / "LICENSE").write_text("MIT")
    data = {"project": {"license": {"file": "LICENSE"}}}
    assert check_files(data, root=tmp_path) == []


def test_license_file_missing(tmp_path: Path) -> None:
    data = {"project": {"license": {"file": "LICENSE"}}}
    diags = check_files(data, root=tmp_path)
    assert any(d.code == "file-missing" for d in diags)


def test_no_files_no_errors(tmp_path: Path) -> None:
    data: dict[str, object] = {"project": {"name": "foo", "version": "1.0.0"}}
    assert check_files(data, root=tmp_path) == []
