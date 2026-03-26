# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Enforce MIT license headers on all source files.

This test prevents drift — every .py file in the project must start with the
copyright and SPDX license header.
"""
from pathlib import Path

EXPECTED_LINE_1 = "# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>"
EXPECTED_LINE_2 = "# SPDX-License-Identifier: MIT"

SEARCH_DIRS = ["src", "plugins", "tests", "example"]


def _collect_py_files():
    root = Path(".")
    files = []
    for d in SEARCH_DIRS:
        search_dir = root / d
        if search_dir.exists():
            files.extend(
                p for p in search_dir.rglob("*.py")
                if "__pycache__" not in str(p)
            )
    return sorted(files)


def test_all_python_files_have_mit_header():
    """Every .py file must start with the MIT copyright + SPDX header."""
    files = _collect_py_files()
    assert files, "No .py files found — check SEARCH_DIRS"

    violations = []
    for path in files:
        content = path.read_text()
        lines = content.splitlines()
        if len(lines) < 2 or lines[0] != EXPECTED_LINE_1 or lines[1] != EXPECTED_LINE_2:
            violations.append(str(path))

    assert not violations, (
        f"{len(violations)} file(s) missing MIT license header:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
