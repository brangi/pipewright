# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Anthropic provider — wraps Claude Agent SDK.

This provider preserves the exact current behavior of pipewright:
MCP memory tools, observability hooks, bypassPermissions, and full
Claude Agent SDK agent loop.
"""
import os
from typing import Callable

from pipewright.providers.base import Provider
from pipewright.providers.types import ProviderStepResult

MODEL_ALIASES = {
    "haiku": "claude-haiku-4-5-20250315",
    "sonnet": "claude-sonnet-4-5-20250929",
    "opus": "claude-opus-4-6",
}


class AnthropicProvider(Provider):
    name = "anthropic"

    def resolve_model(self, alias: str) -> str:
        return MODEL_ALIASES.get(alias, alias)

    def validate_config(self) -> str | None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return "ANTHROPIC_API_KEY not set. Add it to .env or export it."
        return None

    async def run_step(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        tools: list[str],
        max_turns: int,
        max_budget_usd: float,
        on_tool_start: Callable | None = None,
        on_tool_end: Callable | None = None,
    ) -> ProviderStepResult:
        from claude_agent_sdk import (
            query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
        )
        from pipewright.observability.hooks import create_hooks
        from pipewright.memory.mcp_server import create_memory_server

        hooks = create_hooks()
        memory_server = create_memory_server()

        memory_tool_names = [
            "mcp__memory__save_memory",
            "mcp__memory__search_memory",
            "mcp__memory__save_preference",
        ]
        allowed_tools = tools + memory_tool_names

        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            model=model,
            max_turns=max_turns,
            max_budget_usd=max_budget_usd,
            hooks=hooks,
            mcp_servers={"memory": memory_server},
            permission_mode="bypassPermissions",
        )

        step_output = []
        cost = None
        num_turns = 0

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text") and block.text:
                        step_output.append(block.text)
            elif isinstance(message, ResultMessage):
                cost = message.total_cost_usd
                num_turns = message.num_turns

        return ProviderStepResult(
            output_text="\n".join(step_output) if step_output else "(no output)",
            total_cost_usd=cost,
            num_turns=num_turns,
        )
