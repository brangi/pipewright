# Plugin Authoring Guide

This guide covers everything you need to create a pipewright plugin.

## Quick Start

```bash
pipewright init my-plugin
```

This creates:
- `plugins/my_plugin/__init__.py`
- `plugins/my_plugin/workflow.py`
- `tests/test_my_plugin.py`

## Plugin Structure

A plugin is a directory under `plugins/` with a `workflow.py` that exports a
`Workflow` subclass:

```python
from pipewright.workflow import Workflow, Step

class MyPluginWorkflow(Workflow):
    name = "my-plugin"
    description = "Does something useful"
    steps = [
        Step(name="analyze", prompt="...", tools=["Read", "Glob"]),
        Step(name="execute", prompt="...", tools=["Read", "Write"]),
    ]
```

The engine discovers your plugin automatically -- no registration needed.
Plugins are **provider-agnostic** -- the same workflow runs on Anthropic,
OpenAI, Groq, OpenRouter, and Ollama without any changes.

## Step Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | str | yes | -- | Unique step identifier |
| `prompt` | str | yes | -- | Prompt template sent to the AI agent |
| `tools` | list[str] | yes | -- | Tools available to the agent |
| `checkpoint` | bool | no | False | Pause for user review before continuing |
| `model` | str | no | None | Override the default model for this step |
| `max_turns` | int | no | 15 | Maximum agent turns before stopping |
| `context_limit` | int | no | 800 | Max chars from this step's compacted output carried forward |
| `permission_level` | str | no | None (inferred) | `"read"`, `"write"`, or `"full"` — restricts tool access |

## Prompt Templates

Prompts support two template variables:

- `{target}` -- replaced with the user's target argument (file path, issue number, etc.)
- `{context}` -- replaced with accumulated output from prior steps

Example:

```python
Step(
    name="analyze",
    prompt=(
        "Analyze the code at {target}. "
        "Identify key functions, dependencies, and edge cases.\n\n"
        "Context from prior steps:\n{context}"
    ),
    tools=["Read", "Glob", "Grep"],
)
```

## Available Tools

These tools are available across all providers:

| Tool | Description | Use For |
|------|-------------|---------|
| Read | Read file contents | Inspecting source code |
| Write | Create or overwrite files | Generating new files |
| Edit | Make targeted edits to files | Modifying existing code |
| Glob | Find files by pattern | Discovering project structure |
| Grep | Search file contents | Finding patterns in code |
| Bash | Run shell commands | Running tests, git operations |

With the Anthropic provider, tools are provided by the Claude Agent SDK.
With all other providers, pipewright runs identical tool implementations locally.
Your plugin doesn't need to know which provider is being used.

## Model Tiering

Use model aliases to optimize cost. These aliases map to the appropriate model
for whichever provider the user has configured:

- **haiku** -- cheapest and fastest. Use for analysis, file discovery, pattern matching.
- **sonnet** -- balanced. Use for code generation, complex reasoning, reviews.
- **opus** -- most capable. Use for critical decisions, complex refactoring.

```python
steps = [
    Step(name="analyze", prompt="...", tools=["Read"], model="haiku"),
    Step(name="generate", prompt="...", tools=["Write"], model="sonnet"),
]
```

If no model is specified, the user's configured default is used (default: haiku).

**Always use aliases** (`haiku`, `sonnet`, `opus`) instead of provider-specific
model names like `gpt-4o-mini` or `claude-haiku-4-5`. This keeps your plugin
portable across all providers.

## Checkpoints

Set `checkpoint=True` on a step to pause execution for user review. The user
can approve, provide feedback, or abort.

Use checkpoints before:
- Writing or modifying files
- Running generated code
- Making irreversible changes

In non-interactive mode (`-y` flag), checkpoints are auto-approved.

## Permission Levels

Steps can declare a `permission_level` to restrict which tools are available:

| Level | Tools Allowed |
|-------|---------------|
| `read` | Read, Glob, Grep |
| `write` | Read, Glob, Grep, Write, Edit |
| `full` | Read, Glob, Grep, Write, Edit, Bash |

If `permission_level` is not set, the engine infers it from the step's tool
list. A global `max_permission` config cap can block steps that exceed it.

## Context Chaining

Each step's output is **smart-compacted** before being appended to the
`{context}` variable for the next step. Instead of raw truncation, the engine
extracts key information:

- File paths mentioned in the output
- Markdown headers and ALL CAPS section labels
- Lines containing decision/action/error keywords
- Head/tail fallback for unstructured content

The result is capped at `context_limit` chars (default 800). This preserves
the most useful information for downstream steps.

Keep prompts focused so the accumulated context stays useful.

## Workflow Chaining

A workflow can trigger another workflow after completion:

```python
from pipewright.workflow import Workflow, Step, Chain

class MyWorkflow(Workflow):
    name = "my-workflow"
    steps = [...]
    chains = [
        Chain(workflow="test-gen", mode="target"),
    ]
```

Chain modes:
- `"target"` -- passes the last step's output as the target
- `"context"` -- passes the full accumulated context as the target

## Workflow Hooks

Workflows can define lifecycle hooks for logging, cost tracking, validation,
or context injection:

```python
from pipewright.workflow import Workflow, Step, HookContext

class MyWorkflow(Workflow):
    name = "my-workflow"
    description = "Example with hooks"
    steps = [...]

    @staticmethod
    def on_start(ctx: HookContext):
        """Called before the first step runs."""
        print(f"Starting {ctx.workflow_name} on {ctx.target}")

    @staticmethod
    def on_step_complete(ctx: HookContext):
        """Called after each step finishes."""
        if ctx.cost_usd and ctx.cost_usd > 0.50:
            ctx.abort = True  # stop if too expensive

    @staticmethod
    def on_complete(ctx: HookContext):
        """Called after all steps finish."""
        print(f"Done! Total cost: ${ctx.cost_usd:.2f}")
```

`HookContext` fields: `workflow_name`, `step_name`, `step_number`,
`total_steps`, `output_text`, `cost_usd`, `duration_seconds`, `context`,
`target`.

Hooks can:
- Set `ctx.abort = True` to stop the workflow
- Set `ctx.inject_context = "..."` to append extra information to the context

## Memory

Every agent step has access to persistent memory tools automatically:
- `save_memory` -- store learnings and observations
- `search_memory` -- recall past context
- `save_preference` -- remember user preferences

With Anthropic, memory works via MCP. With all other providers, memory works
via function calling. Your plugin doesn't need to handle either case -- it's
automatic.

## Testing Your Plugin

The project convention is one test file per plugin at `tests/test_<name>.py`.
At minimum, test:

1. Workflow has a name and description
2. Steps have names and non-empty prompts
3. Steps have tools assigned
4. Checkpoints are on the right steps

See `tests/test_refactor.py` for a complete example.

## Tips

- Keep steps focused on one task each
- Use haiku for cheap analysis, sonnet for complex generation
- Put checkpoints before any file writes
- Search memory at the start of analysis steps for user preferences
- Test against multiple file types if your plugin is language-agnostic
- Always use model aliases, never provider-specific model names
