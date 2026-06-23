from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from pyproject_doctor.model import Diagnostic

# Curated set of common SPDX license identifiers (PEP 639). This is a vendored
# subset, not the full SPDX list; it covers the OSI-approved identifiers people
# overwhelmingly use in Python packaging. Matching is case-insensitive per the
# SPDX spec, so identifiers are compared after lowercasing.
_SPDX_LICENSE_IDS: frozenset[str] = frozenset(
    {
        "MIT",
        "Apache-2.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "LGPL-2.1-only",
        "LGPL-2.1-or-later",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "MPL-2.0",
        "ISC",
        "Unlicense",
        "CC0-1.0",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "BSL-1.0",
        "Zlib",
        "Python-2.0",
        "PSF-2.0",
    }
)

# Curated set of common SPDX license exception identifiers (used after WITH).
_SPDX_EXCEPTION_IDS: frozenset[str] = frozenset(
    {
        "LLVM-exception",
        "Classpath-exception-2.0",
        "GCC-exception-3.1",
    }
)

# Deprecated SPDX identifiers that PEP 639 says should not be used, mapped to the
# canonical replacement to give an actionable message.
_DEPRECATED_LICENSE_IDS: dict[str, str] = {
    "GPL-2.0": "GPL-2.0-only",
    "GPL-2.0+": "GPL-2.0-or-later",
    "GPL-3.0": "GPL-3.0-only",
    "GPL-3.0+": "GPL-3.0-or-later",
    "LGPL-2.1": "LGPL-2.1-only",
    "LGPL-2.1+": "LGPL-2.1-or-later",
    "LGPL-3.0": "LGPL-3.0-only",
    "LGPL-3.0+": "LGPL-3.0-or-later",
    "AGPL-3.0": "AGPL-3.0-only",
    "AGPL-3.0+": "AGPL-3.0-or-later",
}

_LICENSE_IDS_LOWER: frozenset[str] = frozenset(i.lower() for i in _SPDX_LICENSE_IDS)
_EXCEPTION_IDS_LOWER: frozenset[str] = frozenset(
    i.lower() for i in _SPDX_EXCEPTION_IDS
)
_DEPRECATED_IDS_LOWER: dict[str, str] = {
    k.lower(): v for k, v in _DEPRECATED_LICENSE_IDS.items()
}

_KEY_PATH = "project.license"
_CODE = "license-expression-invalid"

# A bare SPDX identifier token: alphanumerics and the punctuation SPDX permits in
# identifiers (dots, hyphens, plus). An optional trailing '+' is matched so the
# '+' deprecation can be reported with a clear message rather than a parse error.
_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9.+-]+")


def _error(message: str) -> Diagnostic:
    return Diagnostic(
        level="error",
        code=_CODE,
        key_path=_KEY_PATH,
        message=message,
    )


def _tokenize(expression: str) -> list[str] | None:
    """Split an SPDX expression into tokens, or None if an illegal char appears.

    Tokens are parentheses or maximal runs of identifier characters. Whitespace
    separates tokens and is otherwise discarded.
    """
    tokens: list[str] = []
    i = 0
    length = len(expression)
    while i < length:
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char in "()":
            tokens.append(char)
            i += 1
            continue
        match = _IDENTIFIER_RE.match(expression, i)
        if match is None:
            return None
        token = match.group()
        tokens.append(token)
        i = match.end()
    return tokens


def _validate_identifier(token: str) -> Diagnostic | None:
    """Validate one license identifier token. Returns a Diagnostic or None."""
    if token.endswith("+"):
        # PEP 639 disallows the '+' operator. Prefer the '-or-later' canonical
        # form: GPL-3.0+ maps to GPL-3.0-or-later, not GPL-3.0-only.
        suggestion = _DEPRECATED_IDS_LOWER.get(token.lower())
        if suggestion is not None:
            return _error(
                f"license identifier '{token}' uses the deprecated '+' operator;"
                f" PEP 639 disallows it, use '{suggestion}' instead"
            )
        return _error(
            f"license identifier '{token}' uses the deprecated '+' operator;"
            f" PEP 639 disallows it, use the explicit '-or-later' form instead"
        )

    lowered = token.lower()
    if lowered in _DEPRECATED_IDS_LOWER:
        return _error(
            f"license identifier '{token}' is deprecated;"
            f" use '{_DEPRECATED_IDS_LOWER[lowered]}' instead (PEP 639 / SPDX)"
        )
    if lowered not in _LICENSE_IDS_LOWER:
        return _error(
            f"'{token}' is not a known SPDX license identifier"
            f" (project.license must be a valid PEP 639 SPDX expression)"
        )
    return None


def _validate_exception(token: str) -> Diagnostic | None:
    """Validate one exception identifier token (after WITH)."""
    if token.lower() not in _EXCEPTION_IDS_LOWER:
        return _error(
            f"'{token}' is not a known SPDX license exception identifier"
            f" (the identifier after WITH must be a valid SPDX exception)"
        )
    return None


def _parse_expression(tokens: list[str]) -> Diagnostic | None:
    """Validate the SPDX expression grammar over the token stream.

    Grammar (PEP 639, simplified):
        expr        := term (("AND" | "OR") term)*
        term        := "(" expr ")" | license-id ["WITH" exception-id]

    Operators AND/OR/WITH are case-insensitive keywords. Returns the first
    Diagnostic found, or None when the whole expression is well formed.
    """
    position = 0
    length = len(tokens)

    def parse_expr() -> Diagnostic | None:
        nonlocal position
        diagnostic = parse_term()
        if diagnostic is not None:
            return diagnostic
        while position < length:
            token = tokens[position]
            upper = token.upper()
            if upper in ("AND", "OR"):
                position += 1
                if position >= length:
                    return _error(
                        f"license expression ends after operator '{token}';"
                        f" an operator must be followed by a license term"
                    )
                diagnostic = parse_term()
                if diagnostic is not None:
                    return diagnostic
                continue
            break
        return None

    def parse_term() -> Diagnostic | None:
        nonlocal position
        if position >= length:
            return _error(
                "license expression is incomplete; expected a license identifier"
            )
        token = tokens[position]

        if token == "(":
            position += 1
            diagnostic = parse_expr()
            if diagnostic is not None:
                return diagnostic
            if position >= length or tokens[position] != ")":
                return _error(
                    "license expression has unbalanced parentheses;"
                    " a '(' is not closed by a matching ')'"
                )
            position += 1
            return None

        if token == ")":
            return _error(
                "license expression has unbalanced parentheses;"
                " found ')' without a matching '('"
            )

        upper = token.upper()
        if upper in ("AND", "OR", "WITH"):
            return _error(
                f"license expression has a misplaced operator '{token}';"
                f" expected a license identifier here"
            )

        diagnostic = _validate_identifier(token)
        if diagnostic is not None:
            return diagnostic
        position += 1

        # Optional WITH exception clause.
        if position < length and tokens[position].upper() == "WITH":
            position += 1
            if position >= length:
                return _error(
                    "license expression ends after 'WITH';"
                    " expected an SPDX exception identifier"
                )
            exception_token = tokens[position]
            if exception_token in ("(", ")") or exception_token.upper() in (
                "AND",
                "OR",
                "WITH",
            ):
                return _error(
                    f"'WITH' must be followed by an SPDX exception identifier,"
                    f" got '{exception_token}'"
                )
            diagnostic = _validate_exception(exception_token)
            if diagnostic is not None:
                return diagnostic
            position += 1

        return None

    diagnostic = parse_expr()
    if diagnostic is not None:
        return diagnostic

    if position != length:
        leftover = tokens[position]
        if leftover == ")":
            return _error(
                "license expression has unbalanced parentheses;"
                " found ')' without a matching '('"
            )
        return _error(
            f"license expression has a misplaced token '{leftover}';"
            f" expected an operator (AND, OR) or end of expression"
        )
    return None


def check_license_expression(data: Mapping[str, Any]) -> list[Diagnostic]:
    """Validate project.license as a PEP 639 SPDX license expression.

    Only the modern string form is validated (for example `license = "MIT"` or
    `license = "MIT OR Apache-2.0"`). The legacy table form
    (`license = { file = "..." }` or `{ text = "..." }`) is the deprecated
    PEP 621 form and is intentionally not treated as an expression here; file
    existence for the table form is handled by the files check.

    Flags `license-expression-invalid` for an empty expression, an unknown
    license or exception identifier, a deprecated identifier, the PEP-639
    disallowed `+` suffix, a misplaced operator, or unbalanced parentheses. An
    absent license field or a table-form license produces no finding.
    """
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []

    dynamic = project.get("dynamic", [])
    if isinstance(dynamic, list) and "license" in dynamic:
        return []

    value = project.get("license")
    if value is None:
        return []

    # Legacy table form (PEP 621). Not an SPDX expression; handled elsewhere.
    if isinstance(value, dict):
        return []

    if not isinstance(value, str):
        return [
            _error(
                f"project.license must be a string SPDX expression or a table,"
                f" got {type(value).__name__}"
            )
        ]

    if value.strip() == "":
        return [
            _error(
                "project.license is empty; expected a PEP 639 SPDX license expression"
            )
        ]

    tokens = _tokenize(value)
    if tokens is None:
        return [
            _error(
                f"'{value}' contains characters that are not valid in an SPDX"
                f" license expression"
            )
        ]
    if not tokens:
        return [
            _error(
                "project.license is empty; expected a PEP 639 SPDX license expression"
            )
        ]

    diagnostic = _parse_expression(tokens)
    if diagnostic is not None:
        return [diagnostic]
    return []
