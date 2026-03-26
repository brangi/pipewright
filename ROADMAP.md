# Pipewright Roadmap

## v0.1.0 (current)

What ships today:

- CLI-first workflow engine with async step orchestration
- 6 built-in plugins: test-gen, issue-solve, code-review, debug, refactor, docs-gen
- Plugin scaffolding via `pipewright init`
- Workflow chaining, checkpoints, auto-approve (`-y`)
- Persistent memory via MCP tools
- Cost-optimized model tiering (haiku/sonnet/opus per step)
- Observability hooks and terminal display
- 194+ tests, MIT license enforcement

## v0.2.0 -- Multi-Language Examples

Goal: Prove pipewright works on any language, not just Python.

- [ ] Reorganize `example/` directory by language
- [ ] Add JavaScript example with package.json
- [ ] Add TypeScript example with tsconfig
- [ ] Add Java example
- [ ] Add Rust example with Cargo.toml
- [ ] Add Go example with go.mod
- [ ] Add Ruby example

## v0.3.0 -- Language-Aware Plugins

Goal: test-gen (and other plugins) automatically detect the target language and use the correct framework.

- [ ] Update test-gen prompts to detect language from file extension
- [ ] Map languages to default test frameworks (Jest, JUnit, cargo test, go test, RSpec)
- [ ] Audit refactor and code-review prompts for language neutrality
- [ ] Add integration tests for multi-language examples
- [ ] Manual verification: run test-gen on each language example

## v0.4.0 -- Documentation and Community

Goal: Make the project welcoming to contributors and easy to adopt.

- [ ] CONTRIBUTING.md with development setup and plugin guide
- [ ] Plugin authoring guide (docs/PLUGIN_GUIDE.md)
- [ ] Update README with supported languages table
- [ ] Usage guide for new users (docs/USAGE_GUIDE.md)
- [ ] First GitHub release

## v0.5.0 -- Live Demos and Showcase

Goal: Demonstrate pipewright working on realistic projects across languages.

- [ ] Create standalone demo projects (Express API, Rust CLI, Go server, Java utils)
- [ ] Run all 6 workflows on demo projects
- [ ] Capture and publish annotated results with cost breakdowns
- [ ] Link demos from README

## Future

- Provider abstraction (OpenAI, Gemini, local models)
- Parallel step execution within workflows
- Plugin marketplace / registry
- CI/CD integration (GitHub Actions)
- Web dashboard for workflow results
- Streaming output to external tools
