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

## Step Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | str | yes | -- | Unique step identifier |
| `prompt` | str | yes | -- | Prompt template sent to the AI agent |
| `tools` | list[str] | yes | -- | Tools available to the agent |
| `checkpoint` | bool | no | False | Pause for user review before continuing |
| `model` | str | no | None | Override the default model for this step |
| `max_turns` | int | no | 15 | Maximum agent turns before stopping |
| `context_limit` | int | no | 1000 | Max chars from this step's output carried forward |

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

| Tool | Description | Use For |
|------|-------------|---------|
| Read | Read file contents | Inspecting source code |
| Write | Create or overwrite files | Generating new files |
| Edit | Make targeted edits to files | Modifying existing code |
| Glob | Find files by pattern | Discovering project structure |
| Grep | Search file contents | Finding patterns in code |
| Bash | Run shell commands | Running tests, git operations |

## Model Tiering

Use different models per step to optimize cost:

- **haiku** -- cheap and fast. Use for analysis, file discovery, pattern matching.
- **sonnet** -- balanced. Use for code generation, complex reasoning, reviews.
- **opus** -- most capable. Use for critical decisions, complex refactoring.

```python
steps = [
    Step(name="analyze", prompt="...", tools=["Read"], model="haiku"),
    Step(name="generate", prompt="...", tools=["Write"], model="sonnet"),
]
```

If no model is specified, the user's configured default is used (default: haiku).

## Checkpoints

Set `checkpoint=True` on a step to pause execution for user review. The user
can approve, provide feedback, or abort.

Use checkpoints before:
- Writing or modifying files
- Running generated code
- Making irreversible changes

In non-interactive mode (`-y` flag), checkpoints are auto-approved.

## Context Chaining

Each step's output (truncated to `context_limit` chars) is appended to the
`{context}` variable for the next step. This lets later steps build on earlier
analysis without re-reading files.

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
