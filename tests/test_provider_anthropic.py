# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the Anthropic provider."""
import os
from unittest.mock import patch
from pipewright.providers.anthropic import AnthropicProvider


def test_resolve_model_haiku():
    """'haiku' alias resolves to a Claude model ID."""
    p = AnthropicProvider()
    resolved = p.resolve_model("haiku")
    assert "claude" in resolved.lower() or "haiku" in resolved.lower()
    assert resolved != "haiku"


def test_resolve_model_sonnet():
    """'sonnet' alias resolves to a Claude model ID."""
    p = AnthropicProvider()
    resolved = p.resolve_model("sonnet")
    assert resolved != "sonnet"


def test_resolve_model_opus():
    """'opus' alias resolves to a Claude model ID."""
    p = AnthropicProvider()
    resolved = p.resolve_model("opus")
    assert resolved != "opus"


def test_resolve_model_passthrough():
    """Unknown alias passes through unchanged."""
    p = AnthropicProvider()
    assert p.resolve_model("claude-3-5-haiku-20241022") == "claude-3-5-haiku-20241022"


def test_validate_config_missing_key():
    """Returns error when ANTHROPIC_API_KEY is not set."""
    p = AnthropicProvider()
    with patch.dict(os.environ, {}, clear=True):
        # Remove the key if it exists
        os.environ.pop("ANTHROPIC_API_KEY", None)
        error = p.validate_config()
    assert error is not None
    assert "ANTHROPIC_API_KEY" in error


def test_validate_config_ok():
    """Returns None when ANTHROPIC_API_KEY is set."""
    p = AnthropicProvider()
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
        error = p.validate_config()
    assert error is None


def test_provider_name():
    """Provider name is 'anthropic'."""
    assert AnthropicProvider.name == "anthropic"
