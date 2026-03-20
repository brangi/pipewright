"""Workflow and Step base classes.

Plugin authors subclass Workflow to define their own dev automation pipelines.
Each Workflow is a sequence of Steps. Each Step maps to an agent execution.
"""
from dataclasses import dataclass, field


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
    """
    name: str
    prompt: str
    tools: list[str] = field(default_factory=lambda: ["Read", "Glob", "Grep"])
    checkpoint: bool = False
    model: str | None = None


class Workflow:
    """Base class for workflow plugins.

    Subclass this and define `name`, `description`, and `steps` to create
    a new workflow that can be run via `pipewright run <name>`.

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
