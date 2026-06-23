from __future__ import annotations

from pathlib import Path

from pyproject_doctor.checks.license_expression import check_license_expression
from pyproject_doctor.parse import check_file

DATA = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# Unit tests against check_license_expression directly
# ---------------------------------------------------------------------------


def test_valid_simple_no_finding() -> None:
    data = {"project": {"name": "pkg", "license": "MIT"}}
    assert check_license_expression(data) == []


def test_valid_or_no_finding() -> None:
    data = {"project": {"name": "pkg", "license": "MIT OR Apache-2.0"}}
    assert check_license_expression(data) == []


def test_valid_and_no_finding() -> None:
    data = {"project": {"name": "pkg", "license": "Apache-2.0 AND MIT"}}
    assert check_license_expression(data) == []


def test_valid_with_exception_no_finding() -> None:
    data = {"project": {"name": "pkg", "license": "Apache-2.0 WITH LLVM-exception"}}
    assert check_license_expression(data) == []


def test_valid_parenthesized_no_finding() -> None:
    data = {
        "project": {"name": "pkg", "license": "(MIT OR Apache-2.0) AND BSD-3-Clause"}
    }
    assert check_license_expression(data) == []


def test_case_insensitive_operators_and_ids() -> None:
    data = {"project": {"name": "pkg", "license": "mit or apache-2.0"}}
    assert check_license_expression(data) == []


def test_absent_no_finding() -> None:
    data = {"project": {"name": "pkg", "version": "1.0.0"}}
    assert check_license_expression(data) == []


def test_no_project_section_no_finding() -> None:
    data: dict[str, object] = {}
    assert check_license_expression(data) == []


def test_dynamic_license_skipped() -> None:
    data = {"project": {"name": "pkg", "dynamic": ["license"]}}
    assert check_license_expression(data) == []


def test_table_form_not_flagged_as_expression() -> None:
    data = {"project": {"name": "pkg", "license": {"text": "MIT"}}}
    assert check_license_expression(data) == []


def test_table_form_file_not_flagged_as_expression() -> None:
    data = {"project": {"name": "pkg", "license": {"file": "LICENSE"}}}
    assert check_license_expression(data) == []


def test_empty_expression_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "   "}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "empty" in diags[0].message
    assert diags[0].key_path == "project.license"


def test_non_string_license_flagged() -> None:
    data = {"project": {"name": "pkg", "license": 42}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "string" in diags[0].message


def test_unknown_identifier_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "MIT OR Nonsense-9.9"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "Nonsense-9.9" in diags[0].message


def test_unknown_exception_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "Apache-2.0 WITH Bogus-exception"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "exception" in diags[0].message


def test_malformed_operator_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "MIT OR OR Apache-2.0"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"


def test_leading_operator_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "OR MIT"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"


def test_trailing_operator_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "MIT OR"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"


def test_unbalanced_open_paren_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "(MIT OR Apache-2.0"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "parenthes" in diags[0].message


def test_unbalanced_close_paren_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "MIT OR Apache-2.0)"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "parenthes" in diags[0].message


def test_plus_suffix_deprecation_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "GPL-3.0+"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "+" in diags[0].message
    assert "GPL-3.0-or-later" in diags[0].message


def test_deprecated_identifier_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "GPL-3.0"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"
    assert "GPL-3.0-only" in diags[0].message


def test_with_without_exception_flagged() -> None:
    data = {"project": {"name": "pkg", "license": "Apache-2.0 WITH"}}
    diags = check_license_expression(data)
    assert len(diags) == 1
    assert diags[0].code == "license-expression-invalid"


# ---------------------------------------------------------------------------
# Fixture-based integration tests (via parse.check_file)
# ---------------------------------------------------------------------------


def test_fixture_valid_simple() -> None:
    diags = check_file(DATA / "license_valid_simple.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_fixture_valid_or() -> None:
    diags = check_file(DATA / "license_valid_or.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_fixture_valid_and() -> None:
    diags = check_file(DATA / "license_valid_and.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_fixture_valid_with() -> None:
    diags = check_file(DATA / "license_valid_with.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_fixture_valid_parens() -> None:
    diags = check_file(DATA / "license_valid_parens.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_fixture_unknown_id() -> None:
    diags = check_file(DATA / "license_unknown_id.toml")
    codes = {d.code for d in diags}
    assert "license-expression-invalid" in codes


def test_fixture_malformed_operator() -> None:
    diags = check_file(DATA / "license_malformed_operator.toml")
    codes = {d.code for d in diags}
    assert "license-expression-invalid" in codes


def test_fixture_unbalanced_parens() -> None:
    diags = check_file(DATA / "license_unbalanced_parens.toml")
    codes = {d.code for d in diags}
    assert "license-expression-invalid" in codes


def test_fixture_plus_deprecation() -> None:
    diags = check_file(DATA / "license_plus_deprecation.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert len(errors) == 1
    assert "GPL-3.0-or-later" in errors[0].message


def test_fixture_table_form_not_flagged() -> None:
    diags = check_file(DATA / "license_table_form.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []


def test_clean_fixture_has_no_license_expression_finding() -> None:
    diags = check_file(DATA / "clean.toml")
    errors = [d for d in diags if d.code == "license-expression-invalid"]
    assert errors == []
