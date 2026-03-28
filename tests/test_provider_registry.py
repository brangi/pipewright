# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for provider registry."""
import pytest
from pipewright.providers.registry import register, get_provider, available_providers, _PROVIDERS
from pipewright.providers.base import Provider
from pipewright.providers.types import ProviderStepResult


class _DummyProvider(Provider):
    name = "dummy"

    def resolve_model(self, alias):
        return alias

    def validate_config(self):
        return None

    async def run_step(self, **kwargs):
        return ProviderStepResult(output_text="dummy")


def test_anthropic_always_registered():
    """Anthropic is registered by default (core dependency)."""
    # Trigger registration by importing the package
    import pipewright.providers  # noqa: F401
    assert "anthropic" in available_providers()


def test_get_unknown_provider_raises():
    """Requesting an unknown provider raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("nonexistent_provider_xyz")


def test_register_and_get_custom_provider():
    """Custom providers can be registered and retrieved."""
    register("dummy_test", _DummyProvider)
    try:
        provider = get_provider("dummy_test")
        assert provider.name == "dummy"
    finally:
        _PROVIDERS.pop("dummy_test", None)


def test_available_providers_sorted():
    """available_providers returns sorted list."""
    providers = available_providers()
    assert providers == sorted(providers)


def test_available_providers_includes_anthropic():
    """Anthropic is always in the list."""
    import pipewright.providers  # noqa: F401
    assert "anthropic" in available_providers()
