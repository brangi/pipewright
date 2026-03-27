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

## v1.0.0 -- Production Ready

Goal: Make pipewright stable, extensible, and provider-agnostic.

- [ ] Provider abstraction (OpenAI, Gemini, local models via Ollama)
- [ ] Parallel step execution within workflows
- [ ] Plugin registry / marketplace
- [ ] CI/CD integration examples (GitHub Actions workflow plugin)
- [ ] Streaming output to external tools (JSON, webhooks)
- [ ] Configuration validation and schema
- [ ] Comprehensive error recovery and retry strategies
- [ ] Performance benchmarks and optimization

## Future

- Web dashboard for workflow results and history
- Team features (shared memory, workflow templates)
- VS Code / IDE extension
- Self-hosted plugin registry
- Workflow composition (combine plugins into meta-workflows)
