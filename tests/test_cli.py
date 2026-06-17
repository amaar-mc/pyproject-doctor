from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyproject_doctor.cli import run


def test_clean_file_exits_zero(tmp_path: Path) -> None:
    toml = tmp_path / "pyproject.toml"
    toml.write_text('[project]\nname = "foo"\nversion = "1.0.0"\n')
    assert run([str(toml)]) == 0


def test_invalid_file_exits_one(tmp_path: Path) -> None:
    toml = tmp_path / "pyproject.toml"
    toml.write_text('[project]\nversion = "not-valid-version"\n')
    assert run([str(toml)]) == 1


def test_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    toml = tmp_path / "pyproject.toml"
    toml.write_text('[project]\nversion = "bad!!version"\n')
    run([str(toml), "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert any(d["code"] == "version-invalid" for d in data)


def test_missing_file_exits_one() -> None:
    assert run(["/nonexistent/pyproject.toml"]) == 1
