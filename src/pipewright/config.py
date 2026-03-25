# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Configuration management for Pipewright.

Settings are stored in ~/.pipewright/config.json.
API keys come from environment variables (never stored in config).
"""
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current working directory
load_dotenv()

CONFIG_DIR = Path.home() / ".pipewright"
CONFIG_FILE = CONFIG_DIR / "config.json"
MEMORY_DIR = CONFIG_DIR / "memory"

# Defaults applied when no config exists yet
DEFAULTS = {
    "provider": "anthropic",
    "model": "haiku",
    "max_budget_usd": 0.50,
}


def _ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    """Load config, merging saved values over defaults."""
    _ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
        except (json.JSONDecodeError, IOError):
            saved = {}
    else:
        saved = {}
    return {**DEFAULTS, **saved}


def save(cfg: dict):
    """Write config to disk."""
    _ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get(key: str) -> str | None:
    """Get a single config value."""
    return load().get(key)


def set_value(key: str, value: str):
    """Set a single config value and persist."""
    cfg = load()
    # Auto-convert numeric strings
    try:
        value = float(value) if "." in value else int(value)
    except ValueError:
        pass
    cfg[key] = value
    save(cfg)
