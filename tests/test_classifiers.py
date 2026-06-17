from __future__ import annotations

from pyproject_doctor.checks.classifiers import check_classifiers


def test_valid_classifiers() -> None:
    data = {
        "project": {
            "classifiers": [
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
            ]
        }
    }
    # With trove-classifiers installed, these should be valid
    diags = check_classifiers(data)
    error_diags = [d for d in diags if d.level == "error"]
    assert error_diags == []


def test_unknown_classifier() -> None:
    data = {
        "project": {
            "classifiers": ["This :: Is :: Not :: Real"]
        }
    }
    diags = check_classifiers(data)
    # Either we get a classifier-unknown error (if trove-classifiers installed)
    # or a classifiers-skipped info (if not installed)
    assert len(diags) >= 1
    codes = {d.code for d in diags}
    assert codes <= {"classifier-unknown", "classifiers-skipped"}


def test_no_classifiers_no_errors() -> None:
    data = {"project": {"name": "foo"}}
    assert check_classifiers(data) == []
