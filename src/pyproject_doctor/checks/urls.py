from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

from pyproject_doctor.model import Diagnostic


def _is_absolute_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)
    except Exception:
        return False


def check_urls(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Check that all project.urls values are absolute URLs."""
    diagnostics: list[Diagnostic] = []
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []
    urls = project.get("urls", {})
    if not isinstance(urls, dict):
        return []
    for name, url in urls.items():
        if not isinstance(url, str):
            continue
        if not _is_absolute_url(url):
            diagnostics.append(
                Diagnostic(
                    level="error",
                    code="url-invalid",
                    key_path=f"project.urls.{name}",
                    message=f"URL '{url}' is not a valid absolute URL (must have scheme and host)",
                )
            )
    return diagnostics
