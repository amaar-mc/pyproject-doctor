from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyproject_doctor.cli import run
from pyproject_doctor.model import Diagnostic
from pyproject_doctor.sarif import to_sarif


def _diagnostic(level: str, code: str) -> Diagnostic:
    return Diagnostic(
        level=level,  # type: ignore[arg-type]
        code=code,
        key_path="project.version",
        message=f"{code} message",
    )


def test_top_level_structure() -> None:
    doc = to_sarif(
        [_diagnostic("error", "version-invalid")],
        artifact_uri="pyproject.toml",
        tool_version="0.3.0",
    )
    assert doc["version"] == "2.1.0"
    assert doc["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
    runs = doc["runs"]
    assert isinstance(runs, list)
    assert len(runs) == 1
    driver = runs[0]["tool"]["driver"]
    assert driver["name"] == "pyproject-doctor"
    assert driver["version"] == "0.3.0"


def test_rule_id_equals_diagnostic_code() -> None:
    doc = to_sarif(
        [_diagnostic("error", "requires-python-invalid")],
        artifact_uri="pyproject.toml",
        tool_version="0.3.0",
    )
    result = doc["runs"][0]["results"][0]
    assert result["ruleId"] == "requires-python-invalid"
    rule_ids = [r["id"] for r in doc["runs"][0]["tool"]["driver"]["rules"]]
    assert "requires-python-invalid" in rule_ids


def test_file_location_present() -> None:
    doc = to_sarif(
        [_diagnostic("error", "version-invalid")],
        artifact_uri="path/to/pyproject.toml",
        tool_version="0.3.0",
    )
    result = doc["runs"][0]["results"][0]
    uri = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    assert uri == "path/to/pyproject.toml"


def test_level_derived_from_diagnostic_level() -> None:
    doc = to_sarif(
        [
            _diagnostic("error", "version-invalid"),
            _diagnostic("warning", "url-invalid"),
            _diagnostic("info", "classifier-unknown"),
        ],
        artifact_uri="pyproject.toml",
        tool_version="0.3.0",
    )
    results = doc["runs"][0]["results"]
    levels = {r["ruleId"]: r["level"] for r in results}
    assert levels["version-invalid"] == "error"
    assert levels["url-invalid"] == "warning"
    assert levels["classifier-unknown"] == "note"


def test_empty_diagnostics_yields_empty_results() -> None:
    doc = to_sarif([], artifact_uri="pyproject.toml", tool_version="0.3.0")
    assert doc["runs"][0]["results"] == []
    assert doc["runs"][0]["tool"]["driver"]["rules"] == []


def test_cli_sarif_output_is_valid_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    toml = tmp_path / "pyproject.toml"
    toml.write_text('[project]\nversion = "bad!!version"\n')
    run([str(toml), "--format", "sarif"])
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["version"] == "2.1.0"
    results = doc["runs"][0]["results"]
    assert any(r["ruleId"] == "version-invalid" for r in results)
    location = results[0]["locations"][0]["physicalLocation"]["artifactLocation"]
    assert location["uri"] == str(toml)
