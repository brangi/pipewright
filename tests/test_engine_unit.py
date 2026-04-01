# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for engine helper functions."""

from pipewright.engine import _summarize


def test_summarize_read_extracts_filename():
    assert _summarize("Read", {"file_path": "/a/b/c.py"}) == "c.py"


def test_summarize_read_no_slash_returns_whole_path():
    assert _summarize("Read", {"file_path": "simple.py"}) == "simple.py"


def test_summarize_read_missing_file_path_returns_empty():
    assert _summarize("Read", {}) == ""


def test_summarize_glob_returns_pattern():
    assert _summarize("Glob", {"pattern": "**/*.py"}) == "**/*.py"


def test_summarize_grep_wraps_pattern_in_quotes():
    assert _summarize("Grep", {"pattern": "TODO"}) == '"TODO"'


def test_summarize_bash_short_command_unchanged():
    assert _summarize("Bash", {"command": "pytest tests/"}) == "pytest tests/"


def test_summarize_bash_long_command_truncated():
    long_cmd = "x" * 80
    result = _summarize("Bash", {"command": long_cmd})
    assert result == "x" * 60 + "..."
    assert len(result) == 63


def test_summarize_write_extracts_filename():
    assert _summarize("Write", {"file_path": "/a/b.py"}) == "b.py"


def test_summarize_edit_extracts_filename():
    assert _summarize("Edit", {"file_path": "/x/y/z.ts"}) == "z.ts"


def test_summarize_unknown_tool_returns_empty():
    assert _summarize("UnknownTool", {}) == ""
