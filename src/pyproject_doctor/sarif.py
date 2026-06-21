"""Render diagnostics as a SARIF 2.1.0 log.

SARIF (Static Analysis Results Interchange Format) is the format GitHub code scanning
and other tools ingest. The document is built as plain dictionaries so it can be
serialized with the standard library json module and asserted against in tests.

This module is a pure renderer: it takes diagnostics and produces a dict. All IO
(reading the file, printing the JSON) lives in the CLI.
"""

from __future__ import annotations

from pyproject_doctor.model import Diagnostic, Level

_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
_INFORMATION_URI = "https://github.com/amaar-mc/pyproject-doctor"

# SARIF defines three result levels: error, warning, note. Map the Diagnostic
# Level onto them; "info" becomes the SARIF "note" level.
_SARIF_LEVEL_BY_DIAGNOSTIC_LEVEL: dict[Level, str] = {
    "error": "error",
    "warning": "warning",
    "info": "note",
}


def _sarif_level(level: Level) -> str:
    """Map a Diagnostic level onto a SARIF result level (error, warning, note)."""
    return _SARIF_LEVEL_BY_DIAGNOSTIC_LEVEL[level]


def _driver_rules(diagnostics: list[Diagnostic]) -> list[dict[str, object]]:
    """Build the rule catalog from the diagnostic codes actually present.

    Each distinct diagnostic code becomes one SARIF rule, in first-seen order.
    The rule level is taken from the first diagnostic carrying that code.
    """
    rules: list[dict[str, object]] = []
    seen: set[str] = set()
    for diagnostic in diagnostics:
        if diagnostic.code in seen:
            continue
        seen.add(diagnostic.code)
        rules.append(
            {
                "id": diagnostic.code,
                "name": _rule_name(diagnostic.code),
                "shortDescription": {"text": diagnostic.message},
                "defaultConfiguration": {"level": _sarif_level(diagnostic.level)},
            }
        )
    return rules


def _rule_name(code: str) -> str:
    """A PascalCase identifier for the rule, for example version-invalid to VersionInvalid."""
    return "".join(part.capitalize() for part in code.split("-"))


def _result(diagnostic: Diagnostic, *, artifact_uri: str) -> dict[str, object]:
    location: dict[str, object] = {"artifactLocation": {"uri": artifact_uri}}
    result: dict[str, object] = {
        "ruleId": diagnostic.code,
        "level": _sarif_level(diagnostic.level),
        "message": {"text": diagnostic.message},
        "locations": [{"physicalLocation": location}],
    }
    if diagnostic.key_path:
        result["properties"] = {"keyPath": diagnostic.key_path}
    return result


def to_sarif(
    diagnostics: list[Diagnostic], *, artifact_uri: str, tool_version: str
) -> dict[str, object]:
    """Build a SARIF 2.1.0 document for the given diagnostics.

    Each diagnostic maps to one SARIF result. The diagnostic code becomes the
    ruleId, the SARIF level is derived from the diagnostic's level (error,
    warning, info to error, warning, note), and every result points at
    artifact_uri (the pyproject.toml file under analysis).
    """
    return {
        "version": "2.1.0",
        "$schema": _SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "pyproject-doctor",
                        "informationUri": _INFORMATION_URI,
                        "version": tool_version,
                        "rules": _driver_rules(diagnostics),
                    }
                },
                "results": [
                    _result(diagnostic, artifact_uri=artifact_uri)
                    for diagnostic in diagnostics
                ],
            }
        ],
    }
