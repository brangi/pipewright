# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Provider system — multi-LLM support for Pipewright."""
from pipewright.providers.registry import register, get_provider, available_providers  # noqa: F401
from pipewright.providers.base import Provider  # noqa: F401
from pipewright.providers.types import ProviderStepResult  # noqa: F401

# Always register Anthropic (claude-agent-sdk is a core dependency)
from pipewright.providers.anthropic import AnthropicProvider
register("anthropic", AnthropicProvider)

# Conditionally register OpenAI-compatible providers
try:
    from pipewright.providers.openai_compat import (
        OpenAICompatibleProvider,
        OllamaProvider,
        GroqProvider,
        OpenRouterProvider,
    )
    register("openai", OpenAICompatibleProvider)
    register("ollama", OllamaProvider)
    register("groq", GroqProvider)
    register("openrouter", OpenRouterProvider)
except ImportError:
    pass  # openai package not installed; these providers unavailable
