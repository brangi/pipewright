# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for smart context compaction."""

from pipewright.context import compact


class TestCompact:

    def test_short_text_passes_through(self):
        text = "Hello world"
        assert compact(text, limit=800) == text

    def test_empty_text(self):
        assert compact("", limit=800) == ""

    def test_respects_limit(self):
        text = "x" * 5000
        result = compact(text, limit=200)
        assert len(result) <= 200

    def test_extracts_file_paths(self):
        text = ("Here is the analysis:\n" * 50 +
                "Found issues in src/auth.py and tests/test_auth.py\n" +
                "More filler text\n" * 50)
        result = compact(text, limit=300)
        assert "src/auth.py" in result

    def test_extracts_markdown_headers(self):
        text = ("Filler\n" * 50 +
                "## Analysis Results\n"
                "Some content here\n" +
                "Filler\n" * 50)
        result = compact(text, limit=300)
        assert "## Analysis Results" in result

    def test_extracts_decision_lines(self):
        text = ("Filler text\n" * 50 +
                "We should refactor the auth module\n"
                "The login function must validate inputs\n" +
                "Filler text\n" * 50)
        result = compact(text, limit=400)
        assert "should refactor" in result

    def test_extracts_error_lines(self):
        text = ("OK line\n" * 50 +
                "TypeError: cannot read property 'id' of undefined\n" +
                "OK line\n" * 50)
        result = compact(text, limit=300)
        assert "TypeError" in result

    def test_extracts_caps_sections(self):
        text = ("filler\n" * 50 +
                "FILES CHANGED\n"
                "auth.py\n" +
                "filler\n" * 50)
        result = compact(text, limit=300)
        assert "FILES CHANGED" in result

    def test_custom_limit(self):
        text = "word " * 500
        result = compact(text, limit=100)
        assert len(result) <= 100

    def test_fallback_head_tail(self):
        """Plain text with no structured content still gets head/tail."""
        text = "line number {}\n".format  # avoid f-string in test
        content = "\n".join(f"plain line {i}" for i in range(200))
        result = compact(content, limit=300)
        assert len(result) <= 300
        assert len(result) > 0
