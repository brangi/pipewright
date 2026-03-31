# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the pipewright setup command."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from pipewright.cli import main, PROVIDER_INFO


class TestSetupCommand:
    """Tests for pipewright setup."""

    def test_setup_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--help"])
        assert result.exit_code == 0
        assert "Interactive setup" in result.output

    def test_setup_shows_providers(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup"], input="3\nfake-key-123\n")
        assert "Choose an LLM provider" in result.output
        assert "anthropic" in result.output
        assert "groq" in result.output
        assert "openrouter" in result.output
        assert "ollama" in result.output

    def test_setup_groq_saves_key(self, tmp_path):
        config_dir = tmp_path / ".pipewright"
        config_dir.mkdir()

        runner = CliRunner()
        with patch("pipewright.cli.cfg.CONFIG_DIR", config_dir), \
             patch("pipewright.cli.cfg.set_value") as mock_set:
            result = runner.invoke(main, ["setup"], input="3\nfake-groq-key\n")

        assert result.exit_code == 0
        assert "Key saved" in result.output
        assert "Default provider set to: groq" in result.output
        mock_set.assert_called_once_with("provider", "groq")

        env_file = config_dir / ".env"
        assert env_file.exists()
        assert "GROQ_API_KEY=fake-groq-key" in env_file.read_text()

    def test_setup_ollama_no_key_needed(self):
        runner = CliRunner()
        with patch("pipewright.cli.cfg.set_value") as mock_set:
            result = runner.invoke(main, ["setup"], input="5\n")

        assert result.exit_code == 0
        assert "no API key needed" in result.output
        assert "ollama serve" in result.output
        mock_set.assert_called_once_with("provider", "ollama")

    def test_setup_preserves_existing_keys(self, tmp_path):
        config_dir = tmp_path / ".pipewright"
        config_dir.mkdir()
        env_file = config_dir / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=existing-key\n")

        runner = CliRunner()
        with patch("pipewright.cli.cfg.CONFIG_DIR", config_dir), \
             patch("pipewright.cli.cfg.set_value"):
            result = runner.invoke(main, ["setup"], input="3\nnew-groq-key\n")

        content = env_file.read_text()
        assert "ANTHROPIC_API_KEY=existing-key" in content
        assert "GROQ_API_KEY=new-groq-key" in content

    def test_provider_info_complete(self):
        """All 5 providers have required fields."""
        assert len(PROVIDER_INFO) == 5
        for name, info in PROVIDER_INFO.items():
            assert "env_var" in info
            assert "cost" in info
            assert "description" in info
            assert "url" in info
