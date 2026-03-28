# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for engine's provider dispatch logic."""
from unittest.mock import patch, MagicMock
from pipewright.providers import get_provider, available_providers


class TestEngineProviderDispatch:
    """Test that the engine correctly selects and validates providers."""

    def test_default_provider_is_anthropic(self):
        """Config default is 'anthropic'."""
        from pipewright import config as cfg
        config = cfg.load()
        assert config.get("provider", "anthropic") == "anthropic"

    def test_anthropic_provider_instantiates(self):
        """Can instantiate the Anthropic provider."""
        provider = get_provider("anthropic")
        assert provider.name == "anthropic"

    def test_provider_has_required_methods(self):
        """Provider has all required interface methods."""
        provider = get_provider("anthropic")
        assert hasattr(provider, "run_step")
        assert hasattr(provider, "resolve_model")
        assert hasattr(provider, "validate_config")
        assert callable(provider.run_step)
        assert callable(provider.resolve_model)
        assert callable(provider.validate_config)

    def test_unknown_provider_raises(self):
        """Unknown provider name raises ValueError."""
        import pytest
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("nonexistent")

    def test_available_providers_not_empty(self):
        """At least one provider (anthropic) is always available."""
        providers = available_providers()
        assert len(providers) >= 1
        assert "anthropic" in providers

    def test_engine_displays_provider_name(self):
        """Engine would display the provider name (structural check)."""
        # Verify the engine module imports get_provider
        import pipewright.engine as eng
        source = eng.__file__
        from pathlib import Path
        code = Path(source).read_text()
        assert "get_provider" in code
        assert "provider_override" in code
        assert "Provider:" in code
