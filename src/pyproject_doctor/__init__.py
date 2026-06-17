from __future__ import annotations

from pyproject_doctor.checks import check_pyproject
from pyproject_doctor.model import Diagnostic
from pyproject_doctor.parse import check_file

__version__ = "0.2.0"

__all__ = ["check_pyproject", "check_file", "Diagnostic", "__version__"]
