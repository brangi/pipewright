# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for error handling: API key validation, plugin load errors, config corruption."""
import json
import os
from pathlib import Path
from unittest.mock import patch
from pipewright import config as cfg
from pipewright.plugins.loader import discover_plugins


class TestPluginLoadErrors:
    """Test graceful handling of broken plugins."""

    def test_broken_plugin_does_not_crash_loader(self, tmp_path, capsys):
        """A plugin with a SyntaxError is skipped, others still load."""
        good_dir = tmp_path / "good_plugin"
        good_dir.mkdir()
        (good_dir / "__init__.py").write_text("")
        (good_dir / "workflow.py").write_text(
            "from pipewright.workflow import Workflow, Step\n"
            "class GoodWorkflow(Workflow):\n"
            "    name = 'good'\n"
            "    description = 'works'\n"
            "    steps = [Step(name='s1', prompt='test {target} {context}')]\n"
        )

        bad_dir = tmp_path / "bad_plugin"
        bad_dir.mkdir()
        (bad_dir / "__init__.py").write_text("")
        (bad_dir / "workflow.py").write_text("this is not valid python !!!")

        workflows = discover_plugins(tmp_path)
        captured = capsys.readouterr()

        assert "good" in workflows
        assert "failed to load" in captured.out

    def test_import_error_plugin_is_skipped(self, tmp_path, capsys):
        """A plugin with ImportError is skipped gracefully."""
        bad_dir = tmp_path / "bad_import"
        bad_dir.mkdir()
        (bad_dir / "__init__.py").write_text("")
        (bad_dir / "workflow.py").write_text("import nonexistent_module_xyz\n")

        workflows = discover_plugins(tmp_path)
        captured = capsys.readouterr()

        assert "bad_import" not in workflows
        assert "failed to load" in captured.out


class TestConfigCorruption:
    """Test config corruption warning."""

    def test_corrupted_config_warns_user(self, tmp_path, capsys):
        """Corrupted JSON config file prints warning to stderr."""
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json!!!")

        with patch("pipewright.config.CONFIG_FILE", config_file):
            result = cfg.load()

        assert result["model"] == "haiku"
        assert result["provider"] == "anthropic"

        captured = capsys.readouterr()
        assert "corrupted" in captured.err.lower()
