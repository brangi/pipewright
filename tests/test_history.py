# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for workflow history command."""

import json
import time
from unittest.mock import patch

from click.testing import CliRunner

from pipewright.cli import main
from pipewright.observability.display import session_list_row, session_detail
from pipewright.session import Session, create_session


def _make_session(tmp_path, name="test-gen", target="./src", provider="groq",
                  model="haiku", steps=3, complete=False, step_results=None):
    """Helper to create a session with optional completion and results."""
    with patch("pipewright.session.SESSIONS_DIR", tmp_path):
        s = create_session(name, target, provider, model, steps)
        if step_results:
            s.step_results = step_results
            s.current_step = len(step_results)
            s.save()
        if complete:
            s.mark_complete()
    return s


class TestListAll:

    def test_empty_dir(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path / "nope"):
            assert Session.list_all() == []

    def test_returns_completed_and_incomplete(self, tmp_path):
        _make_session(tmp_path, target="./a", complete=False)
        _make_session(tmp_path, target="./b", complete=True)
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all()
        assert len(sessions) == 2

    def test_newest_first(self, tmp_path):
        s1 = _make_session(tmp_path, target="./a")
        time.sleep(0.05)
        s2 = _make_session(tmp_path, target="./b")
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all()
        assert sessions[0].id == s2.id
        assert sessions[1].id == s1.id

    def test_filter_by_workflow(self, tmp_path):
        _make_session(tmp_path, name="test-gen", target="./a")
        _make_session(tmp_path, name="code-review", target="./b")
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all(workflow="code-review")
        assert len(sessions) == 1
        assert sessions[0].workflow_name == "code-review"

    def test_filter_completed(self, tmp_path):
        _make_session(tmp_path, target="./a", complete=True)
        _make_session(tmp_path, target="./b", complete=False)
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all(status="completed")
        assert len(sessions) == 1
        assert sessions[0].completed is True

    def test_filter_incomplete(self, tmp_path):
        _make_session(tmp_path, target="./a", complete=True)
        _make_session(tmp_path, target="./b", complete=False)
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all(status="incomplete")
        assert len(sessions) == 1
        assert sessions[0].completed is False

    def test_limit(self, tmp_path):
        for i in range(5):
            _make_session(tmp_path, target=f"./{i}")
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            sessions = Session.list_all(limit=2)
        assert len(sessions) == 2


class TestClearAll:

    def test_removes_all_files(self, tmp_path):
        _make_session(tmp_path, target="./a")
        _make_session(tmp_path, target="./b")
        _make_session(tmp_path, target="./c")
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            Session.clear_all()
        assert list(tmp_path.glob("*.json")) == []

    def test_returns_count(self, tmp_path):
        _make_session(tmp_path, target="./a")
        _make_session(tmp_path, target="./b")
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            count = Session.clear_all()
        assert count == 2

    def test_empty_dir(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path / "nope"):
            assert Session.clear_all() == 0


class TestHistoryCommand:

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["history", "--help"])
        assert result.exit_code == 0
        assert "history" in result.output.lower()

    def test_no_sessions(self, tmp_path):
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history"])
        assert "No sessions found" in result.output

    def test_lists_sessions(self, tmp_path):
        s = _make_session(tmp_path)
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history"])
        assert s.id in result.output
        assert "test-gen" in result.output

    def test_shows_completed_status(self, tmp_path):
        _make_session(tmp_path, complete=True)
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history"])
        assert "completed" in result.output

    def test_detail_view(self, tmp_path):
        s = _make_session(tmp_path, provider="openrouter", model="sonnet")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", s.id])
        assert s.id in result.output
        assert "test-gen" in result.output
        assert "openrouter" in result.output
        assert "sonnet" in result.output

    def test_detail_not_found(self, tmp_path):
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "nonexistent123"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_filter_workflow(self, tmp_path):
        _make_session(tmp_path, name="test-gen", target="./a")
        _make_session(tmp_path, name="code-review", target="./b")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "-w", "code-review"])
        assert "code-review" in result.output
        assert "1 sessions" in result.output

    def test_filter_status(self, tmp_path):
        _make_session(tmp_path, target="./a", complete=True)
        _make_session(tmp_path, target="./b", complete=False)
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "-s", "completed"])
        assert "1 sessions" in result.output

    def test_limit_flag(self, tmp_path):
        for i in range(5):
            _make_session(tmp_path, target=f"./{i}")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "-l", "2"])
        assert "2 sessions" in result.output

    def test_json_list(self, tmp_path):
        _make_session(tmp_path)
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "--json"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["workflow_name"] == "test-gen"

    def test_json_detail(self, tmp_path):
        s = _make_session(tmp_path)
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", s.id, "--json"])
        data = json.loads(result.output)
        assert data["id"] == s.id
        assert data["workflow_name"] == "test-gen"

    def test_clear_confirm(self, tmp_path):
        _make_session(tmp_path, target="./a")
        _make_session(tmp_path, target="./b")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "clear"], input="y\n")
        assert "Cleared 2 session(s)" in result.output
        assert list(tmp_path.glob("*.json")) == []

    def test_clear_cancel(self, tmp_path):
        _make_session(tmp_path, target="./a")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "clear"], input="n\n")
        assert "Cancelled" in result.output
        assert len(list(tmp_path.glob("*.json"))) == 1

    def test_clear_json_skips_confirm(self, tmp_path):
        _make_session(tmp_path, target="./a")
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["history", "clear", "--json"])
        data = json.loads(result.output)
        assert data["cleared"] == 1


class TestDisplayFormatters:

    def test_list_row_contains_id_and_workflow(self, tmp_path):
        s = _make_session(tmp_path)
        row = session_list_row(s)
        assert s.id in row
        assert "test-gen" in row

    def test_list_row_truncates_long_target(self, tmp_path):
        s = _make_session(tmp_path, target="a" * 50)
        row = session_list_row(s)
        assert "..." in row

    def test_detail_contains_all_fields(self, tmp_path):
        s = _make_session(tmp_path, provider="openai", model="sonnet")
        detail = session_detail(s)
        assert s.id in detail
        assert "test-gen" in detail
        assert "openai" in detail
        assert "sonnet" in detail
        assert "0/3" in detail

    def test_detail_shows_step_costs(self, tmp_path):
        results = [
            {"step_name": "analyze", "step_number": 1, "model": "haiku",
             "output_text": "ok", "cost_usd": 0.05, "num_turns": 3,
             "duration_seconds": 2.5, "skipped": False},
        ]
        s = _make_session(tmp_path, step_results=results)
        detail = session_detail(s)
        assert "analyze" in detail
        assert "$0.0500" in detail
        assert "2.5s" in detail
