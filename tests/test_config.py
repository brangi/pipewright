# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for pipewright.config module.

Tests cover configuration loading, saving, getting/setting values,
default merging, numeric auto-conversion, and corrupted file handling.
All tests use tmp_path to avoid touching the real filesystem.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

import pipewright.config as config_module


@pytest.fixture(autouse=True)
def isolate_config(tmp_path):
    """Redirect CONFIG_DIR, CONFIG_FILE, and MEMORY_DIR to tmp_path."""
    config_dir = tmp_path / ".pipewright"
    config_file = config_dir / "config.json"
    memory_dir = config_dir / "memory"
    with patch.object(config_module, "CONFIG_DIR", config_dir), \
         patch.object(config_module, "CONFIG_FILE", config_file), \
         patch.object(config_module, "MEMORY_DIR", memory_dir):
        yield tmp_path


class TestDefaults:
    """Test the DEFAULTS constant."""

    def test_defaults_has_expected_keys_and_values(self):
        """DEFAULTS should contain provider, model, and max_budget_usd with correct values."""
        assert config_module.DEFAULTS == {
            "provider": "anthropic",
            "model": "haiku",
            "max_budget_usd": 0.50,
        }


class TestLoad:
    """Test the load() function."""

    def test_load_returns_defaults_when_no_config_file(self):
        """load() should return DEFAULTS when no config file exists on disk."""
        cfg = config_module.load()
        assert cfg == config_module.DEFAULTS

    def test_load_merges_saved_values_over_defaults(self):
        """load() should merge saved values on top of DEFAULTS."""
        config_module.save({"provider": "openai"})
        cfg = config_module.load()
        assert cfg["provider"] == "openai"
        assert cfg["model"] == "haiku"
        assert cfg["max_budget_usd"] == 0.50

    def test_load_with_partial_config_preserves_unset_defaults(self):
        """load() with a partial config should keep defaults for unset keys."""
        config_module.save({"model": "sonnet"})
        cfg = config_module.load()
        assert cfg["model"] == "sonnet"
        assert cfg["provider"] == "anthropic"
        assert cfg["max_budget_usd"] == 0.50

    def test_load_corrupted_config_falls_back_to_defaults(self, capsys):
        """load() should return defaults and print a warning for corrupted JSON."""
        config_module._ensure_dirs()
        config_module.CONFIG_FILE.write_text("{not valid json!!!")
        cfg = config_module.load()
        assert cfg == config_module.DEFAULTS
        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "corrupted" in captured.err


class TestSaveLoadRoundtrip:
    """Test save() and load() together."""

    def test_save_then_load_roundtrip(self):
        """Data written by save() should be fully recovered by load()."""
        data = {
            "provider": "groq",
            "model": "opus",
            "max_budget_usd": 1.25,
            "custom_key": "custom_value",
        }
        config_module.save(data)
        loaded = config_module.load()
        for key, value in data.items():
            assert loaded[key] == value


class TestGet:
    """Test the get() function."""

    def test_get_returns_single_value(self):
        """get() should return the value for a known key."""
        assert config_module.get("provider") == "anthropic"

    def test_get_returns_none_for_missing_key(self):
        """get() should return None when the key does not exist."""
        assert config_module.get("nonexistent_key") is None


class TestSetValue:
    """Test the set_value() function."""

    def test_set_value_persists_string(self):
        """set_value() should persist a plain string value."""
        config_module.set_value("provider", "ollama")
        assert config_module.get("provider") == "ollama"

    def test_set_value_auto_converts_int(self):
        """set_value() should auto-convert a numeric string without a dot to int."""
        config_module.set_value("max_turns", "15")
        val = config_module.get("max_turns")
        assert val == 15
        assert isinstance(val, int)

    def test_set_value_auto_converts_float(self):
        """set_value() should auto-convert a numeric string with a dot to float."""
        config_module.set_value("max_budget_usd", "2.75")
        val = config_module.get("max_budget_usd")
        assert val == 2.75
        assert isinstance(val, float)


class TestFindProjectConfig:
    """Test find_project_config() ancestor walk."""

    def test_finds_config_in_start_dir(self, tmp_path):
        project = tmp_path / "myproject"
        project.mkdir()
        cfg_file = project / ".pipewright.json"
        cfg_file.write_text('{"model": "opus"}')
        assert config_module.find_project_config(project) == cfg_file

    def test_finds_config_in_ancestor(self, tmp_path):
        project = tmp_path / "myproject"
        subdir = project / "src" / "deep"
        subdir.mkdir(parents=True)
        cfg_file = project / ".pipewright.json"
        cfg_file.write_text('{"model": "opus"}')
        assert config_module.find_project_config(subdir) == cfg_file

    def test_returns_none_when_absent(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert config_module.find_project_config(empty) is None

    def test_ignores_directories_named_pipewright_json(self, tmp_path):
        """A directory named .pipewright.json should not match."""
        project = tmp_path / "proj"
        project.mkdir()
        (project / ".pipewright.json").mkdir()  # directory, not file
        assert config_module.find_project_config(project) is None


class TestLoadProject:
    """Test load_project() reading and error handling."""

    def test_loads_valid_project_config(self, tmp_path):
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text('{"model": "sonnet", "max_budget_usd": 1.00}')
        result = config_module.load_project(tmp_path)
        assert result == {"model": "sonnet", "max_budget_usd": 1.00}

    def test_returns_empty_when_no_project_config(self, tmp_path):
        assert config_module.load_project(tmp_path) == {}

    def test_corrupted_project_config_returns_empty(self, tmp_path, capsys):
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text("{bad json!!")
        result = config_module.load_project(tmp_path)
        assert result == {}
        assert "corrupted" in capsys.readouterr().err

    def test_non_object_project_config_returns_empty(self, tmp_path, capsys):
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text('["not", "an", "object"]')
        result = config_module.load_project(tmp_path)
        assert result == {}
        assert "not a JSON object" in capsys.readouterr().err


class TestMergeOrder:
    """Test that load() merges defaults → global → project correctly."""

    def test_project_overrides_global(self, tmp_path):
        """Project config should override global config."""
        config_module.save({"model": "haiku", "provider": "openai"})
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text('{"model": "opus"}')
        result = config_module.load(project_dir=tmp_path)
        assert result["model"] == "opus"        # project wins
        assert result["provider"] == "openai"    # global preserved

    def test_global_overrides_defaults(self):
        """Global config should override defaults."""
        config_module.save({"provider": "groq"})
        result = config_module.load()
        assert result["provider"] == "groq"
        assert result["model"] == "haiku"  # default preserved

    def test_partial_project_only_overrides_specified_keys(self, tmp_path):
        """Project config with one key should leave others from global/defaults."""
        config_module.save({"provider": "openai", "model": "sonnet"})
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text('{"max_budget_usd": 0.10}')
        result = config_module.load(project_dir=tmp_path)
        assert result["max_budget_usd"] == 0.10
        assert result["provider"] == "openai"
        assert result["model"] == "sonnet"

    def test_project_can_add_new_keys(self, tmp_path):
        """Project config can introduce keys not in global or defaults."""
        cfg_file = tmp_path / ".pipewright.json"
        cfg_file.write_text('{"max_turns": 5, "context_limit": 500}')
        result = config_module.load(project_dir=tmp_path)
        assert result["max_turns"] == 5
        assert result["context_limit"] == 500
        assert result["provider"] == "anthropic"  # default still there


class TestConfigInit:
    """Test the config init CLI command."""

    def test_config_init_creates_file(self, tmp_path):
        from click.testing import CliRunner
        from pipewright.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            result = runner.invoke(main, ["config", "init"])
            assert result.exit_code == 0
            created = Path(td) / ".pipewright.json"
            assert created.exists()
            data = json.loads(created.read_text())
            assert "model" in data
            assert "provider" in data

    def test_config_init_refuses_overwrite_without_force(self, tmp_path):
        from click.testing import CliRunner
        from pipewright.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            Path(td, ".pipewright.json").write_text("{}")
            result = runner.invoke(main, ["config", "init"])
            assert result.exit_code != 0
            assert "Already exists" in result.output

    def test_config_init_force_overwrites(self, tmp_path):
        from click.testing import CliRunner
        from pipewright.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path) as td:
            Path(td, ".pipewright.json").write_text("{}")
            result = runner.invoke(main, ["config", "init", "--force"])
            assert result.exit_code == 0
            data = json.loads(Path(td, ".pipewright.json").read_text())
            assert "model" in data
