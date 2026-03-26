# Contributing to Pipewright

## Development Setup

```bash
git clone https://github.com/brangi/pipewright.git
cd pipewright
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create a `.env` file with your Anthropic API key:

```bash
echo "ANTHROPIC_API_KEY=sk-..." > .env
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
