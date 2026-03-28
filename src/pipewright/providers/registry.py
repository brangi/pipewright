# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Provider registry — maps provider names to classes."""
from pipewright.providers.base import Provider

_PROVIDERS: dict[str, type[Provider]] = {}


def register(name: str, provider_cls: type[Provider]):
    """Register a provider class by name."""
    _PROVIDERS[name] = provider_cls


def get_provider(name: str) -> Provider:
    """Look up and instantiate a provider by name."""
    if name not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS.keys())) or "(none)"
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")
    return _PROVIDERS[name]()


def available_providers() -> list[str]:
    """Return sorted list of registered provider names."""
    return sorted(_PROVIDERS.keys())
