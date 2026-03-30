# Usage Guide

This guide walks you through using pipewright on your own projects.

## Setup

1. Install pipewright:

```bash
pip install pipewright                # Anthropic only
pip install pipewright[openai]        # + OpenAI, Groq, OpenRouter, Ollama
```

Or from source:

```bash
git clone https://github.com/brangi/pipewright.git && cd pipewright && pip install -e ".[dev,openai]"
```

2. Set your API key (at least one provider):

```bash
# Add to .env in your project root -- pick one or more:
ANTHROPIC_API_KEY=sk-ant-...          # Anthropic (default provider)
OPENAI_API_KEY=sk-proj-...            # OpenAI
GROQ_API_KEY=gsk_...                  # Groq (free tier)
OPENROUTER_API_KEY=sk-or-...          # OpenRouter (free models)
# Ollama needs no key -- just have it running locally
```

3. Verify it works:

```bash
pipewright list
pipewright providers    # see which providers are available
```

## Choosing a Provider

Pipewright supports 5 LLM providers. Choose based on your needs:

| If you want... | Use | Why |
|----------------|-----|-----|
| Best quality | `anthropic` | Claude is the most capable at tool use and code generation |
| Cheapest paid | `openai` | GPT-4o-mini costs ~$0.003 per workflow run |
| Completely free (cloud) | `groq` | Llama 4 Scout via Groq's free tier, no cost |
| Completely free (cloud) | `openrouter` | Auto-selects best available free model |
| Completely free (local) | `ollama` | Run open-source models on your own hardware |
| CI/CD pipelines | `openai` or `groq` | Reliable, fast, cost-effective |

Switch providers with the `-p` flag:

```bash
pipewright run test-gen ./src/auth.py -p groq       # free
pipewright run test-gen ./src/auth.py -p openai     # ~$0.003
pipewright run test-gen ./src/auth.py -p openrouter  # free
```

Or set a default:

```bash
pipewright config set provider groq
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
# File path -- most workflows
pipewright run test-gen ./src/utils.py
pipewright run refactor ./src/auth/

# Git ref -- code-review
pipewright run code-review HEAD~3..HEAD
pipewright run code-review main..feature-branch

# PR number -- code-review
pipewright run code-review "#42"

# Issue number -- issue-solve
pipewright run issue-solve 42

# Error description -- debug
pipewright run debug "TypeError: cannot read property 'id' of undefined in handlers.js"

# Default (current directory) -- any workflow
pipewright run docs-gen
```

## Understanding Output

Each workflow runs in steps. You'll see:

1. **Step banner** -- which step is running and what model is being used
2. **Tool calls** -- the agent reading files, searching code, running commands
3. **Agent output** -- the AI agent's analysis, code, or actions
4. **Checkpoint** -- a pause for your review (approve, provide feedback, or abort)
5. **Result** -- summary of what was done

The header shows your provider and model:

```
Provider: groq | Model: haiku | Budget cap: $0.5
```

### Checkpoints

When a step has a checkpoint, pipewright pauses and asks you to review. You can:
- **Approve** -- continue to the next step
- **Provide feedback** -- the next step will incorporate your input
- **Abort** -- stop the workflow

For CI or non-interactive use, pass `-y` to auto-approve all checkpoints:

```bash
pipewright run test-gen ./src/utils.py -y
```

### Structured Output (JSON)

Pipewright can export workflow results as structured JSON for integration with
dashboards, CI/CD pipelines, Slack bots, or other tools.

**Print JSON to terminal:**

```bash
pipewright run test-gen ./src/utils.py --format json -y
```

**Write JSON to a file:**

```bash
pipewright run test-gen ./src/utils.py -o result.json -y
```

**Pipe JSON to stdout (suppresses terminal output):**

```bash
pipewright run test-gen ./src/utils.py -o - -y 2>/dev/null | jq .
```

The JSON output includes per-step metadata:

```json
{
  "workflow_name": "test-gen",
  "target": "./src/utils.py",
  "provider": "groq",
  "model_alias": "haiku",
  "steps": [
    {
      "step_name": "analyze",
      "step_number": 1,
      "model": "meta-llama/llama-4-scout-17b-16e-instruct",
      "output_text": "Found 3 functions...",
      "cost_usd": null,
      "num_turns": 2,
      "duration_seconds": 4.5,
      "skipped": false
    }
  ],
  "success": true,
  "total_cost_usd": 0.0,
  "total_duration_seconds": 12.3
}

## Cost Expectations

Costs vary significantly by provider:

### Free Providers

| Provider | Cost | Notes |
|----------|------|-------|
| **Groq** | $0.00 | Free tier with rate limits (30 req/min) |
| **OpenRouter** | $0.00 | Uses free model router, rate limited |
| **Ollama** | $0.00 | Runs on your hardware, no API costs |

### Paid Providers

| Provider | Model | Cost/Step | Typical Workflow |
|----------|-------|-----------|-----------------|
| **OpenAI** | gpt-4o-mini (haiku) | $0.001-0.005 | $0.003-0.01 |
| **OpenAI** | gpt-4o (sonnet) | $0.01-0.05 | $0.03-0.10 |
| **Anthropic** | Claude Haiku | $0.01-0.05 | $0.10-0.30 |
| **Anthropic** | Claude Sonnet | $0.05-0.20 | $0.15-0.40 |
| **Anthropic** | Claude Opus | $0.10-0.50 | $0.30-1.00 |

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
language-agnostic -- they adapt to whatever code they're given.

## Tips

- Start with `test-gen` on a small file to see how it works
- Use `-y` for scripted/CI runs where you don't need interactive review
- Try `-p groq` or `-p openrouter` for free runs while experimenting
- Use `pipewright providers` to see which providers are available
- Use `pipewright config set provider openai` to avoid typing `-p` every time
- Run from your project root so the agent can see your full codebase
- The agent has access to your project's virtual environment (auto-detected)
