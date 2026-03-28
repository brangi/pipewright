# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for OpenAI-compatible providers."""
import os
from unittest.mock import patch, MagicMock

import pytest

# These tests cover model aliases and config validation only —
# no actual API calls are made.

try:
    from pipewright.providers.openai_compat import (
        OpenAICompatibleProvider,
        OllamaProvider,
        GroqProvider,
        OpenRouterProvider,
    )
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

pytestmark = pytest.mark.skipif(not HAS_OPENAI, reason="openai package not installed")


# --- Model alias tests --- #

class TestOpenAIAliases:
    def test_haiku_resolves(self):
        p = OpenAICompatibleProvider()
        assert p.resolve_model("haiku") == "gpt-4o-mini"

    def test_sonnet_resolves(self):
        p = OpenAICompatibleProvider()
        assert p.resolve_model("sonnet") == "gpt-4o"

    def test_passthrough(self):
        p = OpenAICompatibleProvider()
        assert p.resolve_model("gpt-4o-mini") == "gpt-4o-mini"


class TestOllamaAliases:
    def test_haiku_resolves(self):
        p = OllamaProvider()
        assert "llama" in p.resolve_model("haiku")

    def test_passthrough(self):
        p = OllamaProvider()
        assert p.resolve_model("codellama:13b") == "codellama:13b"


class TestGroqAliases:
    def test_haiku_resolves(self):
        p = GroqProvider()
        resolved = p.resolve_model("haiku")
        assert "llama" in resolved or "groq" in resolved

    def test_passthrough(self):
        p = GroqProvider()
        assert p.resolve_model("mixtral-8x7b-32768") == "mixtral-8x7b-32768"


class TestOpenRouterAliases:
    def test_haiku_resolves(self):
        p = OpenRouterProvider()
        resolved = p.resolve_model("haiku")
        assert "free" in resolved or "deepseek" in resolved

    def test_passthrough(self):
        p = OpenRouterProvider()
        assert p.resolve_model("anthropic/claude-3.5-sonnet") == "anthropic/claude-3.5-sonnet"


# --- Base URL tests --- #

class TestBaseUrls:
    def test_openai_no_base_url(self):
        assert OpenAICompatibleProvider.base_url is None

    def test_ollama_base_url(self):
        assert "localhost" in OllamaProvider.base_url
        assert "11434" in OllamaProvider.base_url

    def test_groq_base_url(self):
        assert "groq.com" in GroqProvider.base_url

    def test_openrouter_base_url(self):
        assert "openrouter.ai" in OpenRouterProvider.base_url


# --- Config validation tests --- #

class TestConfigValidation:
    def test_openai_missing_key(self):
        p = OpenAICompatibleProvider()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            error = p.validate_config()
        assert error is not None
        assert "OPENAI_API_KEY" in error

    def test_openai_with_key(self):
        """With key set and openai installed, validation passes."""
        p = OpenAICompatibleProvider()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch.dict("sys.modules", {"openai": MagicMock()}):
                error = p.validate_config()
        assert error is None

    def test_ollama_no_key_needed(self):
        """Ollama doesn't require an API key."""
        p = OllamaProvider()
        with patch.dict("sys.modules", {"openai": MagicMock()}):
            error = p.validate_config()
        assert error is None

    def test_groq_missing_key(self):
        p = GroqProvider()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GROQ_API_KEY", None)
            error = p.validate_config()
        assert error is not None
        assert "GROQ_API_KEY" in error

    def test_openrouter_missing_key(self):
        p = OpenRouterProvider()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENROUTER_API_KEY", None)
            error = p.validate_config()
        assert error is not None
        assert "OPENROUTER_API_KEY" in error


# --- Provider names --- #

class TestProviderNames:
    def test_openai_name(self):
        assert OpenAICompatibleProvider.name == "openai"

    def test_ollama_name(self):
        assert OllamaProvider.name == "ollama"

    def test_groq_name(self):
        assert GroqProvider.name == "groq"

    def test_openrouter_name(self):
        assert OpenRouterProvider.name == "openrouter"
