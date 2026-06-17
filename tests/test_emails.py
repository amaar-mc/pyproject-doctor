from __future__ import annotations

import pytest

from pyproject_doctor.checks.emails import check_emails


@pytest.mark.parametrize("email", [
    "user@example.com",
    "user.name+tag@subdomain.example.co.uk",
    "user@example.io",
])
def test_valid_emails(email: str) -> None:
    data = {"project": {"authors": [{"name": "Test", "email": email}]}}
    assert check_emails(data) == []


@pytest.mark.parametrize("email", [
    "not-an-email",
    "@example.com",
    "user@",
    "user@example",
    "user @example.com",
])
def test_invalid_emails(email: str) -> None:
    data = {"project": {"authors": [{"name": "Test", "email": email}]}}
    diags = check_emails(data)
    assert any(d.code == "email-invalid" for d in diags)
