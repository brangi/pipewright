# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for session persistence and resume."""

import json
from unittest.mock import patch

from click.testing import CliRunner

from pipewright.cli import main
from pipewright.session import Session, create_session, SESSIONS_DIR


class TestSession:

    def test_creation(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
        assert s.workflow_name == "test-gen"
        assert s.target == "./src"
        assert s.provider == "groq"
        assert s.current_step == 0
        assert s.total_steps == 3
        assert s.completed is False
        assert len(s.id) == 12

    def test_save_creates_file(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            path = tmp_path / f"{s.id}.json"
            assert path.exists()

    def test_load_roundtrip(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            loaded = Session.load(s.id)
        assert loaded is not None
        assert loaded.id == s.id
        assert loaded.workflow_name == "test-gen"
        assert loaded.target == "./src"

    def test_load_nonexistent(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            assert Session.load("bogus123") is None

    def test_load_corrupted(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            tmp_path.mkdir(exist_ok=True)
            (tmp_path / "bad.json").write_text("not json{{{")
            assert Session.load("bad") is None

    def test_mark_complete(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            s.mark_complete()
            loaded = Session.load(s.id)
        assert loaded.completed is True

    def test_list_recent_excludes_completed(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s1 = create_session("test-gen", "./a", "groq", "haiku", 3)
            s2 = create_session("test-gen", "./b", "groq", "haiku", 3)
            s2.mark_complete()
            recent = Session.list_recent()
        assert len(recent) == 1
        assert recent[0].id == s1.id

    def test_list_recent_newest_first(self, tmp_path):
        import time
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s1 = create_session("test-gen", "./a", "groq", "haiku", 3)
            time.sleep(0.05)
            s2 = create_session("test-gen", "./b", "groq", "haiku", 3)
            recent = Session.list_recent()
        assert recent[0].id == s2.id
        assert recent[1].id == s1.id

    def test_cleanup_keeps_max(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            with patch("pipewright.session.MAX_SESSIONS", 3):
                for i in range(5):
                    create_session("test-gen", f"./{i}", "groq", "haiku", 3)
            files = list(tmp_path.glob("*.json"))
        assert len(files) == 3

    def test_unique_ids(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s1 = create_session("test-gen", "./a", "groq", "haiku", 3)
            s2 = create_session("test-gen", "./b", "groq", "haiku", 3)
        assert s1.id != s2.id

    def test_step_results_roundtrip(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            s.step_results = [
                {"step_name": "analyze", "step_number": 1, "model": "haiku",
                 "output_text": "ok", "cost_usd": 0.01, "num_turns": 2,
                 "duration_seconds": 1.5, "skipped": False},
            ]
            s.save()
            loaded = Session.load(s.id)
        assert len(loaded.step_results) == 1
        assert loaded.step_results[0]["step_name"] == "analyze"


class TestResumeCommand:

    def test_resume_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["resume", "--help"])
        assert result.exit_code == 0
        assert "Resume" in result.output

    def test_resume_no_sessions(self, tmp_path):
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["resume"])
        assert "No resumable sessions" in result.output

    def test_resume_lists_sessions(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            runner = CliRunner()
            result = runner.invoke(main, ["resume"])
        assert s.id in result.output
        assert "test-gen" in result.output

    def test_resume_nonexistent_session(self, tmp_path):
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            result = runner.invoke(main, ["resume", "nonexistent123"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_resume_completed_session(self, tmp_path):
        runner = CliRunner()
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            s.mark_complete()
            result = runner.invoke(main, ["resume", s.id])
        assert result.exit_code != 0
        assert "already completed" in result.output

    def test_resume_listing_shows_step_progress(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 5)
            s.current_step = 2
            s.save()
            runner = CliRunner()
            result = runner.invoke(main, ["resume"])
        assert "2/5" in result.output

    def test_resume_listing_truncates_long_target(self, tmp_path):
        long_target = "a" * 50
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            create_session("test-gen", long_target, "groq", "haiku", 3)
            runner = CliRunner()
            result = runner.invoke(main, ["resume"])
        assert "..." in result.output


class TestSessionEdgeCases:

    def test_session_context_preserved_on_save(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            s.context = "Target: ./src\n--- Result from 'analyze' ---\nfound issues\n"
            s.current_step = 1
            s.save()
            loaded = Session.load(s.id)
        assert "found issues" in loaded.context
        assert loaded.current_step == 1

    def test_session_timestamps_update_on_save(self, tmp_path):
        import time
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("test-gen", "./src", "groq", "haiku", 3)
            first_update = s.updated_at
            time.sleep(0.05)
            s.save()
            assert s.updated_at > first_update

    def test_session_provider_and_model_stored(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path):
            s = create_session("code-review", "HEAD~3..HEAD", "openrouter", "sonnet", 4)
            loaded = Session.load(s.id)
        assert loaded.provider == "openrouter"
        assert loaded.model_alias == "sonnet"
        assert loaded.total_steps == 4

    def test_empty_sessions_dir(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path / "nonexistent"):
            assert Session.list_recent() == []

    def test_cleanup_with_no_dir(self, tmp_path):
        with patch("pipewright.session.SESSIONS_DIR", tmp_path / "nonexistent"):
            Session.cleanup()  # should not raise
