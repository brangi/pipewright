# Pipewright Roadmap

## v0.1.0 (shipped March 19, 2026)

- [x] CLI-first workflow engine with async step orchestration
- [x] 6 built-in plugins: test-gen, issue-solve, code-review, debug, refactor, docs-gen
- [x] Plugin scaffolding via `pipewright init`
- [x] Workflow chaining, checkpoints, auto-approve (`-y`)
- [x] Persistent memory via MCP tools
- [x] Cost-optimized model tiering (haiku/sonnet/opus per step)
- [x] Observability hooks and terminal display
- [x] 155+ tests, MIT license enforcement

## v0.2.0 (shipped March 26, 2026)

- [x] Multi-language examples: Python, JavaScript, TypeScript, Java, Rust, Go, Ruby
- [x] Language-aware test-gen (auto-detects framework from file extension)
- [x] Audited all plugin prompts for language neutrality
- [x] 350 tests generated across 7 languages ($1.00 total)
- [x] Standalone demo projects (Express API, Rust CLI, Go Server, Java Utils)
- [x] Multi-workflow demos: test-gen, code-review, docs-gen, refactor on demo projects
- [x] CONTRIBUTING.md, plugin authoring guide, usage guide
- [x] GitHub Actions CI (pytest on Python 3.11/3.12/3.13)
- [x] PyPI publishing via trusted publishing
- [x] 199+ tests, comprehensive documentation

## v0.3.0 (shipped March 27, 2026)

- [x] Multi-provider support: Anthropic (default), OpenAI, Ollama, Groq, OpenRouter
- [x] Provider abstraction layer with registry pattern
- [x] Full agent loop for OpenAI-compatible providers with tool calling
- [x] Local tool implementations (Read, Write, Edit, Glob, Grep, Bash) for non-Claude providers
- [x] Memory tools work across all providers (MCP for Claude, function-calling for others)
- [x] CLI `--provider` / `-p` flag and `pipewright providers` command
- [x] Model alias resolution per provider (haiku/sonnet/opus map to appropriate models)
- [x] Optional `openai` dependency: `pip install pipewright[openai]`
- [x] Structured output: `--format json` and `--output/-o` for JSON export
- [x] `WorkflowResult` / `StepResult` dataclasses with `to_dict()` / `to_json()`

## v0.4.0 (shipped April 1, 2026)

- [x] Smart context compaction (replaces raw 1000-char truncation with heuristic extraction of file paths, headers, decisions, errors)
- [x] Workflow hooks: `on_start`, `on_step_complete`, `on_complete` with abort and context injection
- [x] Plugin permission levels: `read`, `write`, `full` with config cap (`max_permission`)
- [x] Session persistence and `pipewright resume` command
- [x] Coverage tooling (pytest-cov) and CI coverage reporting
- [x] 412 tests passing, 65% coverage

## v1.0.0 — Production Ready

Goal: Make pipewright stable, reliable, and ready for real-world use.

### Must Have

- [x] Workflow resume (`pipewright resume` — shipped in v0.4.0)
- [x] Workflow history (`pipewright history` — browse past runs)
- [ ] Per-project config (`.pipewright.json` in project root, merged with global)
- [x] Rate limit retry with exponential backoff (429 handling in providers)
- [ ] Dry-run mode (`--dry-run` — preview steps, tools, and estimated cost)
- [ ] Parallel step execution within workflows
- [ ] Webhook delivery and JSONL streaming

### Should Have

- [ ] `--verbose` / `--quiet` CLI flags for output control
- [ ] Token counting per step and workflow (in StepResult/WorkflowResult)
- [ ] Streaming output (real-time text feedback during long steps)
- [ ] Plugin dependency validation (ensure required tools like `gh` exist before running)
- [ ] Configuration validation and schema
- [ ] New plugins: security-scan, ci-gen

## Future

- Remote plugin install from git/PyPI (`pipewright plugin install <url>`)
- Plugin marketplace / registry
- Web dashboard for workflow results and history
- Custom tool definitions per plugin
- VS Code / IDE extension
- Team features (shared memory, workflow templates)
- Cost estimation before execution
- Conditional / skippable steps
