# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""MCP server exposing memory tools to agents.

Agents call these tools during workflow execution to save/retrieve learnings.
Tool names when used: mcp__memory__save_memory, mcp__memory__search_memory, etc.
"""
from claude_agent_sdk import tool, create_sdk_mcp_server
from pipewright.memory.store import MemoryStore

_store = MemoryStore()


@tool(
    name="save_memory",
    description="Save a learning or observation to persistent memory. "
    "Use when you discover a useful pattern, mistake to avoid, or codebase insight.",
    input_schema={"text": str, "category": str, "key": str},
)
async def save_memory(args: dict) -> dict:
    _store.save(category=args["category"], key=args["key"], value=args["text"])
    return {"content": [{"type": "text", "text": f"Saved [{args['category']}]: {args['key']}"}]}


@tool(
    name="search_memory",
    description="Search past learnings and preferences. "
    "Use at the start of a task to recall relevant context.",
    input_schema={"query": str},
)
async def search_memory(args: dict) -> dict:
    results = _store.search(args["query"])
    if not results:
        return {"content": [{"type": "text", "text": "No relevant memories found."}]}
    lines = [f"[{r['category']}] {r['key']}: {r['value']}" for r in results]
    return {"content": [{"type": "text", "text": "Found memories:\n" + "\n".join(lines)}]}


@tool(
    name="save_preference",
    description="Save a user preference to remember across sessions. "
    "Use when the user states a preference like 'use pytest' or 'prefer spaces'.",
    input_schema={"key": str, "value": str},
)
async def save_preference(args: dict) -> dict:
    _store.save(category="preferences", key=args["key"], value=args["value"])
    return {"content": [{"type": "text", "text": f"Preference saved: {args['key']} = {args['value']}"}]}


def create_memory_server():
    """Create MCP server config for ClaudeAgentOptions."""
    return create_sdk_mcp_server(
        name="memory",
        version="1.0.0",
        tools=[save_memory, search_memory, save_preference],
    )
