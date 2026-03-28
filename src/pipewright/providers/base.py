# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Callable

from pipewright.providers.types import ProviderStepResult


class Provider(ABC):
    """Base class for all LLM providers.

    Subclasses implement run_step() to execute a single agent step
    using their specific SDK and agent loop.
    """
    name: str = ""

    @abstractmethod
    async def run_step(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        tools: list[str],
        max_turns: int,
        max_budget_usd: float,
        on_tool_start: Callable | None = None,
        on_tool_end: Callable | None = None,
    ) -> ProviderStepResult:
        """Execute a single agent step and return the result."""
        ...

    @abstractmethod
    def resolve_model(self, alias: str) -> str:
        """Resolve a short alias like 'haiku' to a full model ID."""
        ...

    @abstractmethod
    def validate_config(self) -> str | None:
        """Check if provider is configured. Returns error message or None if OK."""
        ...
