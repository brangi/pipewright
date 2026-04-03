# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""OpenAI-compatible provider — works with OpenAI, Groq, Ollama, OpenRouter.

Implements a full agent loop: send prompt → handle tool calls → execute
tools locally → send results back → repeat until the model stops or
max_turns is reached.
"""
import asyncio
import json
import os
from typing import Callable

from pipewright.providers.base import Provider
from pipewright.providers.types import ProviderStepResult
from pipewright.providers.tools import (
    TOOL_SCHEMAS,
    MEMORY_TOOL_SCHEMAS,
    MEMORY_TOOL_NAMES,
    execute_tool,
    execute_memory_tool,
)

# --------------------------------------------------------------------------- #
# Model alias maps per provider                                                #
# --------------------------------------------------------------------------- #

OPENAI_ALIASES = {
    "haiku": "gpt-4o-mini",
    "sonnet": "gpt-4o",
    "opus": "gpt-4o",
}

OLLAMA_ALIASES = {
    "haiku": "llama3.2:3b",
    "sonnet": "llama3.3:70b",
    "opus": "llama3.3:70b",
}

GROQ_ALIASES = {
    "haiku": "qwen/qwen3-32b",
    "sonnet": "qwen/qwen3-32b",
    "opus": "llama-3.3-70b-versatile",
}

OPENROUTER_ALIASES = {
    "haiku": "stepfun/step-3.5-flash:free",
    "sonnet": "nvidia/nemotron-3-super-120b-a12b:free",
    "opus": "meta-llama/llama-3.3-70b-instruct:free",
}


# --------------------------------------------------------------------------- #
# Base OpenAI-compatible provider                                              #
# --------------------------------------------------------------------------- #

class OpenAICompatibleProvider(Provider):
    """Provider for OpenAI API and compatible services."""
    name = "openai"
    base_url: str | None = None
    api_key_env = "OPENAI_API_KEY"
    model_aliases: dict[str, str] = OPENAI_ALIASES

    def resolve_model(self, alias: str) -> str:
        return self.model_aliases.get(alias, alias)

    def validate_config(self) -> str | None:
        if self.api_key_env and not os.environ.get(self.api_key_env):
            return f"{self.api_key_env} not set. Add it to .env or export it."
        try:
            import openai  # noqa: F401
        except ImportError:
            return (
                "openai package not installed. "
                "Install it with: pip install pipewright[openai]"
            )
        return None

    def _get_client(self):
        """Create an AsyncOpenAI client with the appropriate base URL."""
        from openai import AsyncOpenAI
        kwargs = {"api_key": os.environ.get(self.api_key_env, "dummy")}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return AsyncOpenAI(**kwargs)

    def _build_tool_list(self, tools: list[str]) -> list[dict]:
        """Build OpenAI function-calling tool list from step tool names."""
        active = []
        for schema in TOOL_SCHEMAS:
            if schema["function"]["name"] in tools:
                active.append(schema)
        active.extend(MEMORY_TOOL_SCHEMAS)
        return active

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
        """Run agent loop: send message -> handle tool calls -> repeat."""
        client = self._get_client()
        active_tools = self._build_tool_list(tools)

        tool_instruction = (
            "IMPORTANT: You MUST use the provided tools to interact with files "
            "and the system. NEVER write code directly in your response — always "
            "use the Write tool to create files and the Edit tool to modify them. "
            "When you need to run commands, use the Bash tool.\n\n"
        )
        messages = [
            {"role": "system", "content": tool_instruction + system_prompt},
            {"role": "user", "content": prompt},
        ]

        output_texts = []
        turns = 0

        while turns < max_turns:
            turns += 1

            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
            }
            if active_tools:
                kwargs["tools"] = active_tools
                kwargs["tool_choice"] = "auto"

            # Retry with exponential backoff for rate limits
            response = None
            max_retries = 3
            for attempt in range(max_retries + 1):
                try:
                    response = await client.chat.completions.create(**kwargs)
                    break
                except Exception as api_err:
                    err_str = str(api_err)
                    # Rate limit — retry with backoff
                    if ("429" in err_str or "rate" in err_str.lower()) and attempt < max_retries:
                        wait = 2 ** attempt * 5  # 5s, 10s, 20s
                        await asyncio.sleep(wait)
                        continue
                    # Tool use format error — nudge model and retry turn
                    if "tool_use_failed" in err_str and turns < max_turns:
                        messages.append({
                            "role": "user",
                            "content": (
                                "You must use the Write tool to create files. "
                                "Do not write code in your response. Call the "
                                "Write tool with file_path and content parameters."
                            ),
                        })
                        response = None
                        break
                    raise
            if response is None:
                continue  # tool_use_failed or exhausted — retry outer loop
            choice = response.choices[0]
            message = choice.message

            # Collect assistant text
            if message.content:
                output_texts.append(message.content)

            # If no tool calls, we're done
            if not message.tool_calls:
                break

            # Append assistant message (with tool_calls) to history
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                raw_args = tool_call.function.arguments
                try:
                    arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    if not isinstance(arguments, dict):
                        arguments = {"query": str(arguments)} if tool_name in MEMORY_TOOL_NAMES else {"command": str(arguments)}
                except (json.JSONDecodeError, TypeError):
                    arguments = {}

                # Observability callback
                if on_tool_start:
                    on_tool_start(tool_name, arguments)

                # Execute tool
                try:
                    if tool_name in MEMORY_TOOL_NAMES:
                        result = execute_memory_tool(tool_name, arguments)
                    else:
                        result = execute_tool(tool_name, arguments)
                except Exception as tool_err:
                    result = f"Tool error: {tool_err} (args type={type(arguments).__name__}, raw={raw_args!r})"

                if on_tool_end:
                    on_tool_end(tool_name)

                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        return ProviderStepResult(
            output_text="\n".join(output_texts) if output_texts else "(no output)",
            total_cost_usd=None,
            num_turns=turns,
        )


# --------------------------------------------------------------------------- #
# Provider subclasses for specific services                                    #
# --------------------------------------------------------------------------- #

class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"
    base_url = "http://localhost:11434/v1"
    api_key_env = ""  # Ollama doesn't require a key
    model_aliases = OLLAMA_ALIASES

    def validate_config(self) -> str | None:
        try:
            import openai  # noqa: F401
        except ImportError:
            return (
                "openai package not installed. "
                "Install it with: pip install pipewright[openai]"
            )
        return None

    def _get_client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(base_url=self.base_url, api_key="ollama")


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"
    api_key_env = "GROQ_API_KEY"
    model_aliases = GROQ_ALIASES


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"
    api_key_env = "OPENROUTER_API_KEY"
    model_aliases = OPENROUTER_ALIASES
