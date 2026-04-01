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
