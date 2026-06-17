from __future__ import annotations

import pytest

from pyproject_doctor.checks.urls import check_urls


@pytest.mark.parametrize("url", [
    "https://example.com",
    "http://example.com/path",
    "https://github.com/user/repo",
])
def test_valid_urls(url: str) -> None:
    data = {"project": {"urls": {"Homepage": url}}}
    assert check_urls(data) == []


@pytest.mark.parametrize("url", [
    "not-a-url",
    "example.com",
    "ftp:",
    "",
])
def test_invalid_urls(url: str) -> None:
    data = {"project": {"urls": {"Homepage": url}}}
    diags = check_urls(data)
    assert any(d.code == "url-invalid" for d in diags)
