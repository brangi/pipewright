# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Configuration management for Pipewright.

Global settings are stored in ~/.pipewright/config.json.
Per-project settings live in .pipewright.json (searched from cwd upward).
API keys come from environment variables (never stored in config).

Merge order: defaults → global config → project config.
CLI flags and step-level overrides happen downstream in the engine.
"""
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from ~/.pipewright first, then CWD (CWD overrides)
_global_env = Path.home() / ".pipewright" / ".env"
if _global_env.exists():
    load_dotenv(_global_env)
load_dotenv(override=True)  # CWD .env can override global

CONFIG_DIR = Path.home() / ".pipewright"
CONFIG_FILE = CONFIG_DIR / "config.json"
MEMORY_DIR = CONFIG_DIR / "memory"
PROJECT_CONFIG_NAME = ".pipewright.json"

# Defaults applied when no config exists yet
DEFAULTS = {
    "provider": "anthropic",
    "model": "haiku",
    "max_budget_usd": 0.50,
}


def _ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def find_project_config(start_dir: Path | None = None) -> Path | None:
    """Walk up from *start_dir* (default cwd) looking for .pipewright.json."""
    current = (start_dir or Path.cwd()).resolve()
    while True:
        candidate = current / PROJECT_CONFIG_NAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:  # filesystem root
            return None
        current = parent


def load_project(start_dir: Path | None = None) -> dict:
    """Load project-level config. Returns {} if not found or invalid."""
    path = find_project_config(start_dir)
    if path is None:
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"Warning: project config is not a JSON object ({path}), ignoring.",
                  file=sys.stderr)
            return {}
        return data
    except json.JSONDecodeError:
        print(f"Warning: project config corrupted ({path}), ignoring.",
              file=sys.stderr)
        return {}
    except IOError:
        return {}


def load(project_dir: Path | None = None) -> dict:
    """Load config, merging defaults → global → project."""
    _ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: config file corrupted ({CONFIG_FILE}), using defaults.",
                  file=sys.stderr)
            saved = {}
        except IOError:
            saved = {}
    else:
        saved = {}
    project = load_project(project_dir)
    return {**DEFAULTS, **saved, **project}


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
