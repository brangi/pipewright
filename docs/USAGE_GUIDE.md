# Usage Guide

This guide walks you through using pipewright on your own projects.

## Setup

1. Install pipewright:

```bash
pip install pipewright
# or from source:
git clone https://github.com/brangi/pipewright.git && cd pipewright && pip install -e ".[dev]"
```

2. Set your API key:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

3. Verify it works:

```bash
pipewright list
```

## Choosing a Workflow

| Workflow | When to Use | Target |
|----------|------------|--------|
| test-gen | Generate tests for a file or module | File path |
| issue-solve | Solve a GitHub issue end-to-end | Issue number |
| code-review | Review code changes before merge | File, git ref, or PR number |
| debug | Systematically investigate a bug | Error description or file path |
| refactor | Improve code quality without changing behavior | File or directory |
| docs-gen | Generate documentation for code | File or directory |

## Targeting Files

Pipewright accepts different target types depending on the workflow:

```bash
# File path — most workflows
pipewright run test-gen ./src/utils.py
pipewright run refactor ./src/auth/

# Git ref — code-review
pipewright run code-review HEAD~3..HEAD
pipewright run code-review main..feature-branch

# PR number — code-review
pipewright run code-review "#42"

# Issue number — issue-solve
pipewright run issue-solve 42

# Error description — debug
pipewright run debug "TypeError: cannot read property 'id' of undefined in handlers.js"

# Default (current directory) — any workflow
pipewright run docs-gen
```

## Understanding Output

Each workflow runs in steps. You'll see:

1. **Step banner** — which step is running and what model is being used
2. **Agent output** — the AI agent's analysis, code, or actions
3. **Checkpoint** — a pause for your review (approve, provide feedback, or abort)
4. **Result** — summary of what was done

### Checkpoints

When a step has a checkpoint, pipewright pauses and asks you to review. You can:
- **Approve** — continue to the next step
- **Provide feedback** — the next step will incorporate your input
- **Abort** — stop the workflow

For CI or non-interactive use, pass `-y` to auto-approve all checkpoints:

```bash
pipewright run test-gen ./src/utils.py -y
```

## Cost Expectations

Pipewright uses model tiering to keep costs low:

| Model | Cost Range | Used For |
|-------|-----------|----------|
| Haiku | $0.01-0.05/step | Analysis, file discovery, simple checks |
| Sonnet | $0.05-0.20/step | Code generation, reviews, complex reasoning |

Typical workflow costs:
- **test-gen** (3 steps): $0.10-0.30
- **code-review** (4 steps): $0.15-0.40
- **issue-solve** (5 steps): $0.30-0.70
- **refactor** (4 steps): $0.15-0.50

The budget cap (default $0.50/step) prevents runaway costs. Adjust it:

```bash
pipewright config set max_budget_usd 1.00
```

## Multi-Language Support

Pipewright works with any programming language. The test-gen workflow
automatically detects the language from the file extension and uses
the appropriate test framework:

```bash
pipewright run test-gen ./src/utils.py       # Python -> pytest
pipewright run test-gen ./src/utils.js       # JavaScript -> Jest
pipewright run test-gen ./src/utils.ts       # TypeScript -> Vitest
pipewright run test-gen ./src/Utils.java     # Java -> JUnit 5
pipewright run test-gen ./src/lib.rs         # Rust -> cargo test
pipewright run test-gen ./src/utils.go       # Go -> go test
pipewright run test-gen ./src/utils.rb       # Ruby -> RSpec
```

Other workflows (code-review, refactor, docs-gen, debug) are inherently
language-agnostic — they adapt to whatever code they're given.

## Tips

- Start with `test-gen` on a small file to see how it works
- Use `-y` for scripted/CI runs where you don't need interactive review
- Check `pipewright config get model` to see your default model
- Use `pipewright config set model sonnet` for higher quality at higher cost
- Run from your project root so the agent can see your full codebase
- The agent has access to your project's virtual environment (auto-detected)
