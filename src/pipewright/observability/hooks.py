"""SDK hook callbacks for real-time observability.

These intercept agent events and display them in the terminal.
"""
from claude_agent_sdk import HookMatcher
from pipewright.observability import display


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


async def on_tool_start(input_data, tool_use_id, context):
    name = input_data.get("tool_name", "unknown")
    display.tool_call(name, _summarize(name, input_data.get("tool_input", {})))
    return {}


async def on_tool_end(input_data, tool_use_id, context):
    display.tool_result(input_data.get("tool_name", "unknown"))
    return {}


async def on_agent_start(input_data, tool_use_id, context):
    display.agent_start(input_data.get("agent_type", "subagent"))
    return {}


async def on_agent_stop(input_data, tool_use_id, context):
    display.agent_done(input_data.get("agent_id", "subagent"))
    return {}


def create_hooks() -> dict:
    """Build hooks dict for ClaudeAgentOptions."""
    return {
        "PreToolUse": [HookMatcher(hooks=[on_tool_start])],
        "PostToolUse": [HookMatcher(hooks=[on_tool_end])],
        "SubagentStart": [HookMatcher(hooks=[on_agent_start])],
        "SubagentStop": [HookMatcher(hooks=[on_agent_stop])],
    }
