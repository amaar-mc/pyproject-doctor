from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pyproject_doctor import __version__
from pyproject_doctor.parse import check_file
from pyproject_doctor.sarif import to_sarif


def run(argv: list[str]) -> int:
    """Run the CLI and return an exit code."""
    parser = argparse.ArgumentParser(
        prog="pyproject-doctor",
        description="Offline deep validator for pyproject.toml",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="pyproject.toml",
        help="Path to pyproject.toml (default: pyproject.toml)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args(argv)
    path = Path(args.path)
    diagnostics = check_file(path)

    if args.format == "json":
        print(json.dumps([d.as_dict() for d in diagnostics], indent=2))
    elif args.format == "sarif":
        document = to_sarif(
            diagnostics, artifact_uri=str(path), tool_version=__version__
        )
        print(json.dumps(document, indent=2))
    else:
        for d in diagnostics:
            print(f"{d.level} {d.key_path}: {d.code}: {d.message}")

    return 1 if any(d.level == "error" for d in diagnostics) else 0


def main() -> None:
    """Entry point for the CLI."""
    sys.exit(run(sys.argv[1:]))
