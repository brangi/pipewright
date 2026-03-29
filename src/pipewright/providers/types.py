# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Provider-agnostic message types for the engine."""
import json
from dataclasses import dataclass, field, asdict


@dataclass
class ProviderStepResult:
    """Final result of a single agent step execution.

    Both AnthropicProvider and OpenAICompatProvider produce this type,
    so the engine can consume step results without knowing the provider.
    """
    output_text: str
    total_cost_usd: float | None = None
    num_turns: int = 0


@dataclass
class StepResult:
    """Result of a single step execution with metadata."""
    step_name: str
    step_number: int
    model: str
    output_text: str
    cost_usd: float | None = None
    num_turns: int = 0
    duration_seconds: float = 0.0
    skipped: bool = False


@dataclass
class WorkflowResult:
    """Complete result of a workflow execution."""
    workflow_name: str
    target: str
    provider: str
    model_alias: str
    steps: list[StepResult] = field(default_factory=list)
    success: bool = True
    total_cost_usd: float = 0.0
    total_duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
