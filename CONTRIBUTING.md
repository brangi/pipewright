# Contributing to Pipewright

## Development Setup

```bash
git clone https://github.com/brangi/pipewright.git
cd pipewright
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,openai]"
```

Create a `.env` file with your API keys (at least one provider):

```bash
ANTHROPIC_API_KEY=sk-ant-...          # Anthropic (default)
OPENAI_API_KEY=sk-proj-...            # OpenAI (optional)
GROQ_API_KEY=gsk_...                  # Groq free tier (optional)
OPENROUTER_API_KEY=sk-or-...          # OpenRouter free models (optional)
```

Verify your setup:

```bash
pipewright list          # see available workflows
pipewright providers     # see available providers
```

## Running Tests

```bash
pytest tests/                     # full suite
pytest tests/test_engine.py -v    # single file
pytest -q                         # quiet summary
```

All tests must pass before submitting a PR. The test suite includes:
- Plugin structural tests (steps, prompts, tools)
- Engine and CLI tests
- Provider tests (types, registry, Anthropic, OpenAI-compat, tools)
- License header enforcement (see below)

## Adding a Plugin

The fastest way to create a new plugin:

```bash
pipewright init my-plugin
```

This scaffolds `plugins/my_plugin/workflow.py` and a test file. You can also
create one manually -- see `docs/PLUGIN_GUIDE.md` for the full reference.

Each plugin lives in `plugins/<name>/` and exports a `Workflow` subclass with:
- `name` -- the CLI name (e.g., `"my-plugin"`)
- `description` -- short description shown in `pipewright list`
- `steps` -- list of `Step` objects defining the pipeline

Plugins are provider-agnostic -- they work with all 5 providers automatically.
Use model aliases (`haiku`, `sonnet`, `opus`) instead of provider-specific model names.

Run `pipewright list` to verify your plugin is discovered.

## Code Style

- Follow existing patterns in the codebase
- No specific formatter is enforced, but keep things consistent
- Use type hints for function signatures in Python code

## License Headers

Every `.py` file must start with the MIT license header:

```python
# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT
```

This is enforced by `tests/test_license_headers.py` and will fail CI if
missing. The `pipewright init` scaffold adds headers automatically.

## Pull Request Process

1. Create a branch from `main`
2. Make your changes with clear, focused commits
3. Ensure all tests pass (`pytest -q`)
4. Open a PR against `main` with a description of your changes
5. PRs are reviewed for correctness, test coverage, and consistency
