# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Workflow execution engine.

Takes a Workflow definition and runs it step by step using the configured
LLM provider. Each Step becomes an agent call. Results flow from step to
step via context. Checkpoints pause for user approval.
"""
import asyncio
import time
from pathlib import Path
from pipewright.workflow import Workflow, Step, HookContext
from pipewright.plugins.loader import discover_plugins
from pipewright.observability import display
from pipewright import config as cfg
from pipewright.providers import get_provider
from pipewright.providers.types import StepResult, WorkflowResult
from pipewright.context import compact
from pipewright.session import Session, create_session


# Permission levels: each level includes all tools from lower levels
PERMISSION_TOOLS = {
    "read":  {"Read", "Glob", "Grep"},
    "write": {"Read", "Glob", "Grep", "Write", "Edit"},
    "full":  {"Read", "Glob", "Grep", "Write", "Edit", "Bash"},
}


def _infer_permission(tools: list[str]) -> str:
    """Infer the minimum permission level required by a tool set."""
    tool_set = set(tools)
    if tool_set <= PERMISSION_TOOLS["read"]:
        return "read"
    if tool_set <= PERMISSION_TOOLS["write"]:
        return "write"
    return "full"


def _validate_permissions(step: Step, max_permission: str | None) -> str | None:
    """Validate step tools against its declared permission level and config cap.

    Returns error message if validation fails, None if OK.
    """
    level = step.permission_level or _infer_permission(step.tools)
    tool_set = set(step.tools)
    allowed = PERMISSION_TOOLS.get(level, PERMISSION_TOOLS["full"])

    # Check tools match declared level
    excess = tool_set - allowed
    if excess:
        return (f"Step '{step.name}' declares permission '{level}' "
                f"but uses tools beyond that level: {excess}")

    # Check against config cap
    if max_permission:
        level_order = ["read", "write", "full"]
        if level_order.index(level) > level_order.index(max_permission):
            return (f"Step '{step.name}' requires '{level}' permission "
                    f"but max_permission is '{max_permission}'")

    return None


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
                       provider_override: str | None = None,
                       resume_session_id: str | None = None) -> WorkflowResult | None:
    """Execute a workflow against a target.

    Args:
        workflow: The Workflow instance to run
        target: File or directory the user wants to process
        model_override: Optional model override for all steps
        plugins_dir: Directory to discover plugins from (default: cwd/plugins)
        auto_approve: Skip checkpoint prompts (for CI/non-interactive use)
        provider_override: Override the provider (anthropic, openai, ollama, groq, openrouter)

    Returns:
        WorkflowResult with structured execution data, or None on early failure.
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
        return None

    # Validate provider configuration
    config_error = provider.validate_config()
    if config_error:
        display.error(config_error)
        if provider_name == "anthropic":
            display.info("Hint: Create a .env file with: ANTHROPIC_API_KEY=sk-...")
        return None

    default_model_alias = model_override or config.get("model", "haiku")
    max_budget = config.get("max_budget_usd", 0.50)
    max_permission = config.get("max_permission")

    display.workflow_start(workflow.name, workflow.description)
    display.info(f"Target: {target}")
    display.info(f"Provider: {provider_name} | Model: {default_model_alias} | Budget cap: ${max_budget}")

    # Context accumulates results from each step (initialized before hooks)
    context = f"Target: {target}\n"

    # on_start hook
    if workflow.on_start:
        hook_ctx = HookContext(
            workflow_name=workflow.name, target=target,
            total_steps=len(workflow.steps),
        )
        workflow.on_start(hook_ctx)
        if hook_ctx.abort:
            display.error("Workflow aborted by on_start hook.")
            return None
        if hook_ctx.inject_context:
            context += hook_ctx.inject_context + "\n"

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

    result_text = "(no output)"  # last step's output for chain target mode

    # Track structured results
    workflow_start = time.time()
    step_results: list[StepResult] = []

    # Session management (resume or create)
    session = None
    start_step = 0
    if resume_session_id:
        session = Session.load(resume_session_id)
        if not session:
            display.error(f"Session '{resume_session_id}' not found.")
            return None
        context = session.context
        start_step = session.current_step
        for sr_dict in session.step_results:
            step_results.append(StepResult(**sr_dict))
        display.info(f"Resuming session {resume_session_id} from step {start_step + 1}")
    else:
        session = create_session(workflow.name, target, provider_name,
                                 default_model_alias, len(workflow.steps))
        display.info(f"Session: {session.id}")

    for i, step in enumerate(workflow.steps, 1):
        # Skip completed steps on resume
        if i - 1 < start_step:
            display.info(f"Skipping completed step '{step.name}' ({i}/{len(workflow.steps)})")
            continue

        display.step_banner(step.name, i, len(workflow.steps))

        # Validate permissions
        perm_error = _validate_permissions(step, max_permission)
        if perm_error:
            display.error(perm_error)
            step_results.append(StepResult(
                step_name=step.name, step_number=i, model="",
                output_text="(blocked by permissions)", skipped=True,
            ))
            wf_duration = time.time() - workflow_start
            total_cost = sum(s.cost_usd for s in step_results if s.cost_usd)
            return WorkflowResult(
                workflow_name=workflow.name, target=target,
                provider=provider_name, model_alias=default_model_alias,
                steps=step_results, success=False,
                total_cost_usd=total_cost, total_duration_seconds=wf_duration,
            )

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

        step_start = time.time()

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
                    step_results.append(StepResult(
                        step_name=step.name, step_number=i, model=step_model,
                        output_text="(aborted)", skipped=True,
                        duration_seconds=time.time() - step_start,
                    ))
                    wf_duration = time.time() - workflow_start
                    total_cost = sum(s.cost_usd for s in step_results if s.cost_usd)
                    return WorkflowResult(
                        workflow_name=workflow.name, target=target,
                        provider=provider_name, model_alias=default_model_alias,
                        steps=step_results, success=False,
                        total_cost_usd=total_cost, total_duration_seconds=wf_duration,
                    )
                elif response.lower() in ("retry", "r", "y", "yes"):
                    display.info("Retrying step...")
                    step_start = time.time()  # reset timer for retry
                    continue  # re-run this step
                else:
                    # Default: skip this step
                    result = None
                    break
            break  # success: exit retry loop

        step_duration = time.time() - step_start

        # Show results
        result_text = result.output_text if result else "(skipped)"
        display.result_box(f"Step: {step.name}", result_text[:2000])  # Truncate for display

        # Record structured step result
        step_results.append(StepResult(
            step_name=step.name,
            step_number=i,
            model=step_model,
            output_text=result_text,
            cost_usd=result.total_cost_usd if result else None,
            num_turns=result.num_turns if result else 0,
            duration_seconds=step_duration,
            skipped=result is None,
        ))

        # on_step_complete hook
        if workflow.on_step_complete:
            hook_ctx = HookContext(
                workflow_name=workflow.name, step_name=step.name,
                step_number=i, total_steps=len(workflow.steps),
                output_text=result_text, context=context, target=target,
                cost_usd=result.total_cost_usd if result else None,
                duration_seconds=step_duration,
            )
            workflow.on_step_complete(hook_ctx)
            if hook_ctx.abort:
                display.error(f"Workflow aborted by on_step_complete hook after '{step.name}'.")
                wf_duration = time.time() - workflow_start
                total_cost = sum(s.cost_usd for s in step_results if s.cost_usd)
                return WorkflowResult(
                    workflow_name=workflow.name, target=target,
                    provider=provider_name, model_alias=default_model_alias,
                    steps=step_results, success=False,
                    total_cost_usd=total_cost, total_duration_seconds=wf_duration,
                )
            if hook_ctx.inject_context:
                context += hook_ctx.inject_context + "\n"

        # Add to context for next step (smart compaction instead of raw truncation)
        ctx_limit = step.context_limit if step.context_limit is not None else config.get("context_limit", 800)
        compacted = compact(result_text, limit=ctx_limit)
        context += f"\n--- Result from '{step.name}' ---\n{compacted}\n"

        # Persist session state after each step
        if session:
            from dataclasses import asdict
            session.context = context
            session.current_step = i  # 1-based, so this points past the completed step
            session.step_results = [asdict(sr) for sr in step_results]
            session.save()

        # Checkpoint: pause for user if configured
        if step.checkpoint and not auto_approve:
            response = display.checkpoint_prompt(
                f"Step '{step.name}' complete. Review above and continue?"
            )
            if response.lower() in ("n", "no", "abort"):
                display.error("Workflow stopped by user.")
                wf_duration = time.time() - workflow_start
                total_cost = sum(s.cost_usd for s in step_results if s.cost_usd)
                return WorkflowResult(
                    workflow_name=workflow.name, target=target,
                    provider=provider_name, model_alias=default_model_alias,
                    steps=step_results, success=False,
                    total_cost_usd=total_cost, total_duration_seconds=wf_duration,
                )
            elif response and response.lower() not in ("y", "yes", ""):
                # User gave feedback — append to context for next step
                context += f"\nUser feedback: {response}\n"
                display.info(f"Feedback noted: {response}")
        elif step.checkpoint and auto_approve:
            display.info(f"Checkpoint '{step.name}' auto-approved")

    display.success(f"Workflow '{workflow.name}' complete!")

    # Mark session complete
    if session:
        session.mark_complete()

    # on_complete hook
    if workflow.on_complete:
        wf_duration_so_far = time.time() - workflow_start
        total_cost_so_far = sum(s.cost_usd for s in step_results if s.cost_usd)
        hook_ctx = HookContext(
            workflow_name=workflow.name, target=target,
            total_steps=len(workflow.steps), context=context,
            cost_usd=total_cost_so_far, duration_seconds=wf_duration_so_far,
        )
        workflow.on_complete(hook_ctx)

    # Build final workflow result
    wf_duration = time.time() - workflow_start
    total_cost = sum(s.cost_usd for s in step_results if s.cost_usd)
    workflow_result = WorkflowResult(
        workflow_name=workflow.name,
        target=target,
        provider=provider_name,
        model_alias=default_model_alias,
        steps=step_results,
        success=True,
        total_cost_usd=total_cost,
        total_duration_seconds=wf_duration,
    )

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

    return workflow_result


def run(workflow: Workflow, target: str, model_override: str | None = None,
        plugins_dir: Path | None = None, auto_approve: bool = False,
        provider_override: str | None = None,
        resume_session_id: str | None = None) -> WorkflowResult | None:
    """Sync wrapper for run_workflow."""
    return asyncio.run(run_workflow(workflow, target, model_override, plugins_dir,
                                    auto_approve, provider_override,
                                    resume_session_id))
