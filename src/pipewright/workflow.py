# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Workflow and Step base classes.

Plugin authors subclass Workflow to define their own dev automation pipelines.
Each Workflow is a sequence of Steps. Each Step maps to an agent execution.
"""
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Step:
    """A single step in a workflow pipeline.

    Each step runs one agent with a focused task. Steps execute sequentially,
    and each step can access results from previous steps via {context}.

    Args:
        name: Human-readable step name (e.g., "analyze", "generate", "run")
        prompt: The prompt template sent to the agent. Use {target} for the
                user-provided target and {context} for results from prior steps.
        tools: SDK tools this agent can use (e.g., ["Read", "Glob", "Grep"])
        checkpoint: If True, pause and show results to user before continuing.
        model: Override the model for this step (e.g., "haiku" for cheap steps).
        max_turns: Override max agent turns for this step (default: use config).
        context_limit: Override context truncation limit in chars (default: use config).
    """
    name: str
    prompt: str
    tools: list[str] = field(default_factory=lambda: ["Read", "Glob", "Grep"])
    checkpoint: bool = False
    model: str | None = None
    max_turns: int | None = None
    context_limit: int | None = None
    permission_level: str | None = None  # "read", "write", "full" (inferred from tools if None)


@dataclass
class Chain:
    """A chain links one workflow to another.

    After a workflow completes, each chain triggers a follow-up workflow.

    Args:
        workflow: Name of the workflow to run next (must be a discovered plugin).
        mode: How to pass data to the chained workflow.
              "target" — last step's full output becomes the new target.
              "context" — full accumulated context becomes the new target.
    """
    workflow: str
    mode: str = "target"


@dataclass
class HookContext:
    """Data passed to workflow hooks.

    Hooks receive a snapshot of the current execution state. They can set
    ``abort = True`` to stop the workflow or ``inject_context`` to append
    extra information to the context passed to subsequent steps.
    """
    workflow_name: str
    step_name: str | None = None
    step_number: int | None = None
    total_steps: int | None = None
    output_text: str | None = None
    cost_usd: float | None = None
    duration_seconds: float | None = None
    context: str = ""
    target: str = ""
    abort: bool = False
    inject_context: str | None = None


class Workflow:
    """Base class for workflow plugins.

    Subclass this and define `name`, `description`, and `steps` to create
    a new workflow that can be run via `pipewright run <name>`.

    Hooks (optional):
        on_start: Called before the first step runs.
        on_step_complete: Called after each step finishes.
        on_complete: Called after all steps finish.

    Example:
        class MyWorkflow(Workflow):
            name = "my-workflow"
            description = "Does something useful"
            steps = [
                Step(name="step1", prompt="...", tools=["Read"]),
                Step(name="step2", prompt="...", tools=["Write"]),
            ]
    """
    name: str = ""
    description: str = ""
    steps: list[Step] = []
    chains: list[Chain] = []
    on_start: Callable[[HookContext], None] | None = None
    on_step_complete: Callable[[HookContext], None] | None = None
    on_complete: Callable[[HookContext], None] | None = None
