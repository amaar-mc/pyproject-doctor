from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found]

from pyproject_doctor.checks import check_pyproject
from pyproject_doctor.model import Diagnostic


def check_file(path: Path) -> list[Diagnostic]:
    """Parse a pyproject.toml file and run all checks."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return [
            Diagnostic(
                level="error",
                code="file-missing",
                key_path="",
                message=f"File not found: {path}",
            )
        ]
    except Exception as e:
        return [
            Diagnostic(
                level="error",
                code="parse-error",
                key_path="",
                message=f"Failed to parse TOML: {e}",
            )
        ]
    return check_pyproject(data, root=path.parent)
