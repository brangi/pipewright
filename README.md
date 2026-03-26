# Pipewright

CLI-first, plugin-based AI dev workflow automation. Chain AI agents into
multi-step pipelines where each step is focused, checkpointed, and cost-optimized.

## Install

```bash
pip install pipewright
```

Or from source:

```bash
git clone https://github.com/brangi/pipewright.git
cd pipewright
pip install -e ".[dev]"
```

Requires Python 3.11+ and an Anthropic API key:

```bash
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

## Usage

Generate tests for a source file:

```bash
pipewright run test-gen ./src/auth.py
```

Solve a GitHub issue end-to-end (analyze, plan, implement, open PR):

```bash
pipewright run issue-solve 42
```

Review code changes:

```bash
pipewright run code-review HEAD~1..HEAD
pipewright run code-review "#2"
```

Debug an issue systematically:

```bash
pipewright run debug "TypeError in auth.py line 42"
```

Refactor code:

```bash
pipewright run refactor ./src/auth.py
```

Generate documentation:

```bash
pipewright run docs-gen ./src/
```

List all available workflows:

```bash
pipewright list
```

Auto-approve checkpoints for CI/scripted use:

```bash
pipewright run test-gen ./src/auth.py -y
```

## Create a Plugin

Scaffold a new plugin:

```bash
pipewright init my-plugin
```

Or manually -- create `plugins/my_plugin/workflow.py`:

```python
from pipewright.workflow import Workflow, Step

class MyPluginWorkflow(Workflow):
    name = "my-plugin"
    description = "Does something useful"
    steps = [
        Step(name="analyze", prompt="Analyze {target}.\n\n{context}",
             tools=["Read", "Glob"], model="haiku"),
        Step(name="execute", prompt="Execute on {target}.\n\n{context}",
             tools=["Read", "Write"], model="sonnet", checkpoint=True),
    ]
```

Run `pipewright list` to verify it appears.

## Architecture

```
CLI (Click)
  |
  v
Plugin Loader ---- plugins/*/workflow.py
  |
  v
Engine (async orchestrator)
  |
  +---> Step 1: Agent (Claude SDK) ---> context
  +---> Step 2: Agent (Claude SDK) ---> context
  +---> Step 3: Agent (Claude SDK) ---> context (checkpoint)
  |
  v
Result (with memory persistence via MCP)
```

Each step runs a Claude agent with a focused prompt. Steps chain via context
accumulation. Checkpoints pause for human review. Model tiering (haiku for
cheap steps, sonnet for complex) keeps costs low.

## Project Structure

```
src/pipewright/
  cli.py            CLI entry point (Click)
  engine.py         Async orchestrator
  workflow.py       Step, Chain, Workflow dataclasses
  config.py         JSON config (~/.pipewright/config.json)
  plugins/loader.py Plugin discovery
  memory/           Persistent memory (JSON + MCP server)
  observability/    Terminal display and SDK hooks

plugins/
  test_gen/         Generate test suites
  issue_solve/      Solve GitHub issues end-to-end
  code_review/      Review code changes
  refactor/         Refactor code
  docs_gen/         Generate documentation
  debug/            Systematic debugging
```

## Configuration

```bash
pipewright config set model sonnet
pipewright config set max_budget_usd 1.00
pipewright config get model
```

Settings stored in `~/.pipewright/config.json`. API keys come from
environment variables or `.env` (never stored in config).

## License

MIT -- see [LICENSE](LICENSE).
