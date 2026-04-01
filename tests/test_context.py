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

    def test_multiple_extraction_types(self):
        """A single text with files, headers, and decisions extracts all."""
        text = (
            "filler\n" * 30 +
            "## Summary\n"
            "We should update src/auth.py\n"
            "Created tests/test_auth.py\n"
            "filler\n" * 30
        )
        result = compact(text, limit=400)
        assert "## Summary" in result
        assert "src/auth.py" in result
        assert "should update" in result or "Created" in result

    def test_deduplicates_key_lines(self):
        """Repeated lines should not appear multiple times."""
        text = ("We should fix this\n" * 100)
        result = compact(text, limit=400)
        assert result.count("We should fix this") <= 2  # once in key lines, maybe once in fallback

    def test_multiple_file_extensions(self):
        """Extracts files with different extensions."""
        text = (
            "filler\n" * 30 +
            "Modified app.tsx and config.yaml and main.rs\n" +
            "filler\n" * 30
        )
        result = compact(text, limit=400)
        assert "app.tsx" in result
        assert "config.yaml" in result
        assert "main.rs" in result

    def test_exact_limit_boundary(self):
        """Text exactly at limit passes through."""
        text = "x" * 800
        assert compact(text, limit=800) == text

    def test_one_char_over_limit(self):
        """Text one char over limit gets compacted."""
        text = "x" * 801
        result = compact(text, limit=800)
        assert len(result) <= 800

    def test_preserves_warning_lines(self):
        text = (
            "ok\n" * 50 +
            "WARNING: deprecated function used in auth.py\n" +
            "ok\n" * 50
        )
        result = compact(text, limit=300)
        assert "WARNING" in result or "deprecated" in result

    def test_mixed_structured_and_plain_text(self):
        """Structured content is extracted; plain filler is discarded."""
        text = (
            "This is plain text without keywords\n" * 40 +
            "## Important Section\n"
            "We should migrate to the new API\n"
            "Error: connection timeout in main.py\n" +
            "This is plain text without keywords\n" * 40
        )
        result = compact(text, limit=400)
        assert "## Important Section" in result
        assert "should migrate" in result

    def test_compact_always_returns_string(self):
        """Return type is always str regardless of input."""
        assert isinstance(compact("", limit=100), str)
        assert isinstance(compact("short", limit=100), str)
        assert isinstance(compact("x" * 5000, limit=100), str)

    def test_plain_text_no_extraction_still_returns_content(self):
        """Totally unstructured text still produces a non-empty result."""
        text = "\n".join(f"line number {i} with boring content" for i in range(200))
        result = compact(text, limit=300)
        assert len(result) > 0
        assert len(result) <= 300
