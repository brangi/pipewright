# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Workflow execution engine.

Takes a Workflow definition and runs it step by step using the Claude Agent SDK.
Each Step becomes an agent call. Results flow from step to step via context.
Checkpoints pause for user approval.
"""
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
from pipewright.workflow import Workflow, Step
from pipewright.plugins.loader import discover_plugins
from pipewright.observability import display
from pipewright.observability.hooks import create_hooks
from pipewright.memory.mcp_server import create_memory_server
from pipewright import config as cfg


async def run_workflow(workflow: Workflow, target: str, model_override: str | None = None,
                       plugins_dir: Path | None = None):
    """Execute a workflow against a target.

    Args:
        workflow: The Workflow instance to run
        target: File or directory the user wants to process
        model_override: Optional model override for all steps
        plugins_dir: Directory to discover plugins from (default: cwd/plugins)
    """
    if plugins_dir is None:
        plugins_dir = Path.cwd() / "plugins"
    config = cfg.load()
    default_model = model_override or config.get("model", "haiku")
    max_budget = config.get("max_budget_usd", 0.50)

    display.welcome()
    display.info(f"Workflow: {workflow.name} — {workflow.description}")
    display.info(f"Target: {target}")
    display.info(f"Model: {default_model} | Budget cap: ${max_budget}")

    # Context accumulates results from each step
    context = f"Target: {target}\n"
    hooks = create_hooks()
    memory_server = create_memory_server()

    # Memory tool names for allowed_tools
    memory_tools = [
        "mcp__memory__save_memory",
        "mcp__memory__search_memory",
        "mcp__memory__save_preference",
    ]

    result_text = "(no output)"  # last step's output for chain target mode

    for i, step in enumerate(workflow.steps, 1):
        display.step_banner(step.name, i, len(workflow.steps))

        # Build the prompt with context from prior steps
        prompt = step.prompt.replace("{target}", target).replace("{context}", context)

        step_model = step.model or default_model
        allowed_tools = step.tools + memory_tools
        max_turns = step.max_turns if step.max_turns is not None else config.get("max_turns", 15)

        options = ClaudeAgentOptions(
            system_prompt=f"You are a specialist agent executing step '{step.name}' "
                          f"of the '{workflow.name}' workflow. Be focused and thorough.",
            allowed_tools=allowed_tools,
            model=step_model,
            max_turns=max_turns,
            max_budget_usd=max_budget,
            hooks=hooks,
            mcp_servers={"memory": memory_server},
            permission_mode="bypassPermissions",
        )

        # Retry loop — user can retry failed steps
        step_output = []
        while True:
            step_output = []  # clear on each attempt
            try:
                async for message in query(prompt=prompt, options=options):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if hasattr(block, "text") and block.text:
                                step_output.append(block.text)
                    elif isinstance(message, ResultMessage):
                        cost = f"${message.total_cost_usd:.4f}" if message.total_cost_usd else "n/a"
                        display.info(f"Step cost: {cost} | Turns: {message.num_turns}")
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
                    break
            break  # success: exit retry loop

        # Show results
        result_text = "\n".join(step_output) if step_output else "(no output)"
        display.result_box(f"Step: {step.name}", result_text[:2000])  # Truncate for display

        # Add to context for next step
        ctx_limit = step.context_limit if step.context_limit is not None else config.get("context_limit", 1000)
        context += f"\n--- Result from '{step.name}' ---\n{result_text[:ctx_limit]}\n"

        # Checkpoint: pause for user if configured
        if step.checkpoint:
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
        await run_workflow(workflows[chain.workflow], new_target, model_override, plugins_dir)


def run(workflow: Workflow, target: str, model_override: str | None = None,
        plugins_dir: Path | None = None):
    """Sync wrapper for run_workflow."""
    asyncio.run(run_workflow(workflow, target, model_override, plugins_dir))
