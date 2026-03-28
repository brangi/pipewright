# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Provider-agnostic message types for the engine."""
from dataclasses import dataclass


@dataclass
class ProviderStepResult:
    """Final result of a single agent step execution.

    Both AnthropicProvider and OpenAICompatProvider produce this type,
    so the engine can consume step results without knowing the provider.
    """
    output_text: str
    total_cost_usd: float | None = None
    num_turns: int = 0
