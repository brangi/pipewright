# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for local tool implementations (Read, Write, Edit, Glob, Grep, Bash)."""
import os
from pathlib import Path
from unittest.mock import patch

from pipewright.providers.tools import (
    execute_tool,
    execute_memory_tool,
    TOOL_SCHEMAS,
    MEMORY_TOOL_SCHEMAS,
)


# --- Read tool --- #

class TestReadTool:
    def test_read_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\n")
        result = execute_tool("Read", {"file_path": str(f)})
        assert "line1" in result
        assert "line2" in result

    def test_read_with_numbered_lines(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello\nworld\n")
        result = execute_tool("Read", {"file_path": str(f)})
        assert "1" in result
        assert "hello" in result

    def test_read_nonexistent(self):
        result = execute_tool("Read", {"file_path": "/nonexistent/path/file.txt"})
        assert "Error" in result

    def test_read_with_offset_and_limit(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("a\nb\nc\nd\ne\n")
        result = execute_tool("Read", {"file_path": str(f), "offset": 2, "limit": 2})
        assert "b" in result
        assert "c" in result
        assert "a" not in result


# --- Write tool --- #

class TestWriteTool:
    def test_write_creates_file(self, tmp_path):
        f = tmp_path / "new.txt"
        result = execute_tool("Write", {"file_path": str(f), "content": "hello world"})
        assert f.read_text() == "hello world"
        assert "Wrote" in result

    def test_write_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "sub" / "dir" / "file.txt"
        execute_tool("Write", {"file_path": str(f), "content": "nested"})
        assert f.read_text() == "nested"


# --- Edit tool --- #

class TestEditTool:
    def test_edit_replaces_string(self, tmp_path):
        f = tmp_path / "edit.txt"
        f.write_text("hello world")
        result = execute_tool("Edit", {
            "file_path": str(f),
            "old_string": "world",
            "new_string": "pipewright",
        })
        assert f.read_text() == "hello pipewright"
        assert "Edited" in result

    def test_edit_not_found(self, tmp_path):
        f = tmp_path / "edit.txt"
        f.write_text("hello world")
        result = execute_tool("Edit", {
            "file_path": str(f),
            "old_string": "missing",
            "new_string": "replacement",
        })
        assert "not found" in result

    def test_edit_nonexistent_file(self):
        result = execute_tool("Edit", {
            "file_path": "/nonexistent/file.txt",
            "old_string": "a",
            "new_string": "b",
        })
        assert "Error" in result


# --- Glob tool --- #

class TestGlobTool:
    def test_glob_finds_files(self, tmp_path):
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")
        (tmp_path / "c.txt").write_text("")
        result = execute_tool("Glob", {"pattern": "*.py", "path": str(tmp_path)})
        assert "a.py" in result
        assert "b.py" in result
        assert "c.txt" not in result

    def test_glob_no_matches(self, tmp_path):
        result = execute_tool("Glob", {"pattern": "*.xyz", "path": str(tmp_path)})
        assert "No files" in result


# --- Grep tool --- #

class TestGrepTool:
    def test_grep_finds_pattern(self, tmp_path):
        f = tmp_path / "search.txt"
        f.write_text("hello world\nfoo bar\nhello again\n")
        result = execute_tool("Grep", {"pattern": "hello", "path": str(f)})
        assert "hello" in result

    def test_grep_no_matches(self, tmp_path):
        f = tmp_path / "search.txt"
        f.write_text("nothing here\n")
        result = execute_tool("Grep", {"pattern": "missing_pattern_xyz", "path": str(f)})
        assert "No matches" in result.lower() or "missing_pattern_xyz" not in result


# --- Bash tool --- #

class TestBashTool:
    def test_bash_runs_command(self):
        result = execute_tool("Bash", {"command": "echo hello"})
        assert "hello" in result

    def test_bash_captures_stderr(self):
        result = execute_tool("Bash", {"command": "echo error >&2"})
        assert "error" in result

    def test_bash_timeout(self):
        result = execute_tool("Bash", {"command": "sleep 5", "timeout": 1})
        assert "timed out" in result.lower() or "Error" in result


# --- Unknown tool --- #

def test_execute_unknown_tool():
    result = execute_tool("NonexistentTool", {})
    assert "Unknown tool" in result


# --- Memory tools --- #

class TestMemoryTools:
    def test_save_memory(self, tmp_path):
        with patch("pipewright.providers.tools._memory_store") as mock_store:
            result = execute_memory_tool("save_memory", {
                "text": "test insight",
                "category": "testing",
                "key": "test-key",
            })
        assert "Saved" in result
        mock_store.save.assert_called_once()

    def test_search_memory_no_results(self, tmp_path):
        with patch("pipewright.providers.tools._memory_store") as mock_store:
            mock_store.search.return_value = []
            result = execute_memory_tool("search_memory", {"query": "test"})
        assert "No relevant" in result

    def test_search_memory_with_results(self):
        with patch("pipewright.providers.tools._memory_store") as mock_store:
            mock_store.search.return_value = [
                {"category": "testing", "key": "k1", "value": "v1"},
            ]
            result = execute_memory_tool("search_memory", {"query": "test"})
        assert "Found memories" in result
        assert "k1" in result

    def test_save_preference(self):
        with patch("pipewright.providers.tools._memory_store") as mock_store:
            result = execute_memory_tool("save_preference", {
                "key": "style",
                "value": "pytest",
            })
        assert "Preference saved" in result

    def test_unknown_memory_tool(self):
        result = execute_memory_tool("nonexistent", {})
        assert "Unknown" in result


# --- Schema validation --- #

class TestToolSchemas:
    def test_all_tool_schemas_have_name(self):
        for schema in TOOL_SCHEMAS:
            assert "function" in schema
            assert "name" in schema["function"]

    def test_all_memory_schemas_have_name(self):
        for schema in MEMORY_TOOL_SCHEMAS:
            assert "function" in schema
            assert "name" in schema["function"]

    def test_expected_tools_present(self):
        names = {s["function"]["name"] for s in TOOL_SCHEMAS}
        assert names == {"Read", "Write", "Edit", "Glob", "Grep", "Bash"}

    def test_expected_memory_tools_present(self):
        names = {s["function"]["name"] for s in MEMORY_TOOL_SCHEMAS}
        assert names == {"save_memory", "search_memory", "save_preference"}
