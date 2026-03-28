# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Workflow execution engine.

Takes a Workflow definition and runs it step by step using the configured
LLM provider. Each Step becomes an agent call. Results flow from step to
step via context. Checkpoints pause for user approval.
"""
import asyncio
from pathlib import Path
from pipewright.workflow import Workflow, Step
from pipewright.plugins.loader import discover_plugins
from pipewright.observability import display
from pipewright import config as cfg
from pipewright.providers import get_provider


def _summarize(tool_name: str, tool_input: dict) -> str:
    """Short human-readable summary of a tool call."""
    if tool_name == "Read":
        path = tool_input.get("file_path", "")
        return path.split("/")[-1] if "/" in path else path
    elif tool_name == "Glob":
        return tool_input.get("pattern", "")
    elif tool_name == "Grep":
        return f'"{tool_input.get("pattern", "")}"'
    elif tool_name == "Bash":
        cmd = tool_input.get("command", "")
        return cmd[:60] + "..." if len(cmd) > 60 else cmd
    elif tool_name in ("Edit", "Write"):
        path = tool_input.get("file_path", "")
        return path.split("/")[-1] if "/" in path else path
    return ""


async def run_workflow(workflow: Workflow, target: str, model_override: str | None = None,
                       plugins_dir: Path | None = None, auto_approve: bool = False,
                       provider_override: str | None = None):
    """Execute a workflow against a target.

    Args:
        workflow: The Workflow instance to run
        target: File or directory the user wants to process
        model_override: Optional model override for all steps
        plugins_dir: Directory to discover plugins from (default: cwd/plugins)
        auto_approve: Skip checkpoint prompts (for CI/non-interactive use)
        provider_override: Override the provider (anthropic, openai, ollama, groq, openrouter)
    """
    if plugins_dir is None:
        plugins_dir = Path.cwd() / "plugins"
    config = cfg.load()

    # Resolve provider
    provider_name = provider_override or config.get("provider", "anthropic")
    try:
        provider = get_provider(provider_name)
    except ValueError as e:
        display.error(str(e))
        return

    # Validate provider configuration
    config_error = provider.validate_config()
    if config_error:
        display.error(config_error)
        if provider_name == "anthropic":
            display.info("Hint: Create a .env file with: ANTHROPIC_API_KEY=sk-...")
        return

    default_model_alias = model_override or config.get("model", "haiku")
    max_budget = config.get("max_budget_usd", 0.50)

    display.workflow_start(workflow.name, workflow.description)
    display.info(f"Target: {target}")
    display.info(f"Provider: {provider_name} | Model: {default_model_alias} | Budget cap: ${max_budget}")

    # Detect project environment (venv, working directory)
    project_root = plugins_dir.parent if plugins_dir else Path.cwd()
    env_context = f"Project root: {project_root}\n"

    # Check for common venv locations
    venv_python = None
    for venv_name in [".venv", "venv"]:
        candidate = project_root / venv_name / "bin" / "python3"
        if candidate.exists():
            venv_python = candidate
            break

    if venv_python:
        env_context += f"Python executable: {venv_python} (use this for running Python commands)\n"

    # Context accumulates results from each step
    context = f"Target: {target}\n"

    result_text = "(no output)"  # last step's output for chain target mode

    for i, step in enumerate(workflow.steps, 1):
        display.step_banner(step.name, i, len(workflow.steps))

        # Build the prompt with context from prior steps
        prompt = step.prompt.replace("{target}", target).replace("{context}", context)

        step_model_alias = step.model or default_model_alias
        step_model = provider.resolve_model(step_model_alias)
        max_turns = step.max_turns if step.max_turns is not None else config.get("max_turns", 15)

        system_prompt = (
            f"You are a specialist agent executing step '{step.name}' "
            f"of the '{workflow.name}' workflow. Be focused and thorough.\n\n"
            f"Environment context:\n{env_context}"
        )

        # Retry loop — user can retry failed steps
        while True:
            try:
                result = await provider.run_step(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=step_model,
                    tools=step.tools,
                    max_turns=max_turns,
                    max_budget_usd=max_budget,
                    on_tool_start=lambda name, args: display.tool_call(name, _summarize(name, args)),
                    on_tool_end=lambda name: display.tool_result(name),
                )
                cost = f"${result.total_cost_usd:.4f}" if result.total_cost_usd else "n/a"
                display.info(f"Step cost: {cost} | Turns: {result.num_turns}")
            except Exception as e:
                display.error(f"Step '{step.name}' failed: {e}")
                response = display.checkpoint_prompt("Retry this step, skip it, or abort?")
                if response.lower() in ("abort", "n", "no"):
                    display.error("Workflow aborted.")
                    return
                elif response.lower() in ("retry", "r", "y", "yes"):
                    display.info("Retrying step...")
                    continue  # re-run this step
                else:
                    # Default: skip this step
                    result = None
                    break
            break  # success: exit retry loop

        # Show results
        result_text = result.output_text if result else "(skipped)"
        display.result_box(f"Step: {step.name}", result_text[:2000])  # Truncate for display

        # Add to context for next step
        ctx_limit = step.context_limit if step.context_limit is not None else config.get("context_limit", 1000)
        context += f"\n--- Result from '{step.name}' ---\n{result_text[:ctx_limit]}\n"

        # Checkpoint: pause for user if configured
        if step.checkpoint and not auto_approve:
            response = display.checkpoint_prompt(
                f"Step '{step.name}' complete. Review above and continue?"
            )
            if response.lower() in ("n", "no", "abort"):
                display.error("Workflow stopped by user.")
                return
            elif response and response.lower() not in ("y", "yes", ""):
                # User gave feedback — append to context for next step
                context += f"\nUser feedback: {response}\n"
                display.info(f"Feedback noted: {response}")
        elif step.checkpoint and auto_approve:
            display.info(f"Checkpoint '{step.name}' auto-approved")

    display.success(f"Workflow '{workflow.name}' complete!")

    # Execute chained workflows
    for chain in workflow.chains:
        workflows = discover_plugins(plugins_dir)
        if chain.workflow not in workflows:
            display.error(f"Chained workflow '{chain.workflow}' not found, skipping")
            continue

        if chain.mode == "context":
            new_target = context
        else:
            new_target = result_text

        display.info(f"Chaining → {chain.workflow}")
        await run_workflow(workflows[chain.workflow], new_target, model_override, plugins_dir,
                           auto_approve, provider_override)


def run(workflow: Workflow, target: str, model_override: str | None = None,
        plugins_dir: Path | None = None, auto_approve: bool = False,
        provider_override: str | None = None):
    """Sync wrapper for run_workflow."""
    asyncio.run(run_workflow(workflow, target, model_override, plugins_dir,
                             auto_approve, provider_override))
