# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tool implementations for non-Claude providers.

These replicate the Read, Write, Edit, Glob, Grep, Bash tools
that Claude Agent SDK provides natively. They execute locally
and return string results for the agent loop.
"""
import glob as glob_module
import re
import subprocess
from pathlib import Path

from pipewright.memory.store import MemoryStore

# --------------------------------------------------------------------------- #
# OpenAI function-calling schemas                                              #
# --------------------------------------------------------------------------- #

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read a file from the filesystem. Returns numbered lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to read",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file, creating parent directories as needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Edit",
            "description": "Replace a specific string in a file with new content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to edit",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact text to find and replace",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The text to replace it with",
                    },
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Glob",
            "description": "Find files matching a glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g. '**/*.py', 'src/*.rs')",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (defaults to current dir)",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Grep",
            "description": "Search for a regex pattern in files. Returns matching lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Filter files by glob pattern (e.g. '*.py')",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Bash",
            "description": "Execute a shell command and return stdout + stderr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run",
                    },
                },
                "required": ["command"],
            },
        },
    },
]

MEMORY_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": (
                "Save a learning or observation to persistent memory. "
                "Use when you discover a useful pattern, mistake to avoid, or insight."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Content to save"},
                    "category": {"type": "string", "description": "Category label"},
                    "key": {"type": "string", "description": "Short key name"},
                },
                "required": ["text", "category", "key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": (
                "Search past learnings and preferences. "
                "Use at the start of a task to recall relevant context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_preference",
            "description": (
                "Save a user preference to remember across sessions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Preference name"},
                    "value": {"type": "string", "description": "Preference value"},
                },
                "required": ["key", "value"],
            },
        },
    },
]


# --------------------------------------------------------------------------- #
# File system tool implementations                                             #
# --------------------------------------------------------------------------- #

def _tool_read(args: dict) -> str:
    """Read a file with optional offset and limit."""
    file_path = args.get("file_path", "")
    p = Path(file_path)
    if not p.exists():
        return f"Error: File not found: {file_path}"
    if not p.is_file():
        return f"Error: Not a file: {file_path}"
    try:
        lines = p.read_text(errors="replace").splitlines()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

    offset = max(args.get("offset", 1), 1) - 1  # convert to 0-based
    limit = args.get("limit", len(lines) - offset)
    selected = lines[offset:offset + limit]

    numbered = []
    for i, line in enumerate(selected, start=offset + 1):
        truncated = line[:2000] if len(line) > 2000 else line
        numbered.append(f"{i:>6}\t{truncated}")
    return "\n".join(numbered)


def _tool_write(args: dict) -> str:
    """Write content to a file."""
    file_path = args.get("file_path", "")
    content = args.get("content", "")
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} bytes to {file_path}"


def _tool_edit(args: dict) -> str:
    """Replace old_string with new_string in a file."""
    file_path = args.get("file_path", "")
    old_string = args.get("old_string", "")
    new_string = args.get("new_string", "")
    p = Path(file_path)
    if not p.exists():
        return f"Error: File not found: {file_path}"
    text = p.read_text()
    if old_string not in text:
        return f"Error: old_string not found in {file_path}"
    count = text.count(old_string)
    if count > 1:
        return f"Error: old_string found {count} times in {file_path} (must be unique)"
    text = text.replace(old_string, new_string, 1)
    p.write_text(text)
    return f"Edited {file_path}"


def _tool_glob(args: dict) -> str:
    """Find files matching a glob pattern."""
    pattern = args.get("pattern", "")
    search_path = args.get("path", ".")
    full_pattern = str(Path(search_path) / pattern)
    matches = sorted(glob_module.glob(full_pattern, recursive=True))
    if not matches:
        return "No files matched."
    return "\n".join(matches[:200])


def _tool_grep(args: dict) -> str:
    """Search for a pattern in files."""
    pattern = args.get("pattern", "")
    search_path = args.get("path", ".")
    file_glob = args.get("glob", "")

    # Try using grep command first (faster for large directories)
    cmd = ["grep", "-rn", "--include", file_glob, pattern, search_path] if file_glob else \
          ["grep", "-rn", pattern, search_path]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
        )
        output = result.stdout
        if not output:
            return "No matches found."
        # Limit output
        lines = output.splitlines()
        if len(lines) > 100:
            return "\n".join(lines[:100]) + f"\n... ({len(lines)} total matches)"
        return output
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Fallback to Python regex
        return _grep_python(pattern, search_path, file_glob)


def _grep_python(pattern: str, search_path: str, file_glob: str) -> str:
    """Python fallback for grep."""
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Invalid regex: {e}"
    results = []
    root = Path(search_path)
    glob_pattern = file_glob or "**/*"
    for fp in root.glob(glob_pattern):
        if not fp.is_file():
            continue
        try:
            for i, line in enumerate(fp.read_text(errors="replace").splitlines(), 1):
                if regex.search(line):
                    results.append(f"{fp}:{i}:{line}")
                    if len(results) >= 100:
                        return "\n".join(results) + "\n... (truncated at 100 matches)"
        except Exception:
            continue
    return "\n".join(results) if results else "No matches found."


def _tool_bash(args: dict) -> str:
    """Run a shell command."""
    command = args.get("command", "")
    timeout = args.get("timeout", 120)
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout,
        )
        output = result.stdout + result.stderr
        if len(output) > 30000:
            output = output[:30000] + "\n... (output truncated)"
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s"
    except Exception as e:
        return f"Error running command: {e}"


# --------------------------------------------------------------------------- #
# Dispatch                                                                     #
# --------------------------------------------------------------------------- #

_TOOL_HANDLERS = {
    "Read": _tool_read,
    "Write": _tool_write,
    "Edit": _tool_edit,
    "Glob": _tool_glob,
    "Grep": _tool_grep,
    "Bash": _tool_bash,
}


def execute_tool(name: str, arguments) -> str:
    """Execute a file-system tool by name."""
    # Normalize: some models return a string instead of a dict
    if isinstance(arguments, str):
        arguments = {"file_path": arguments, "pattern": arguments,
                     "command": arguments, "path": arguments}
    handler = _TOOL_HANDLERS.get(name)
    if not handler:
        return f"Unknown tool: {name}"
    try:
        return handler(arguments)
    except Exception as e:
        return f"Tool error ({name}): {e}"


# --------------------------------------------------------------------------- #
# Memory tool dispatch (no MCP, uses MemoryStore directly)                     #
# --------------------------------------------------------------------------- #

_memory_store = MemoryStore()

MEMORY_TOOL_NAMES = {"save_memory", "search_memory", "save_preference"}


def execute_memory_tool(name: str, arguments) -> str:
    """Execute a memory tool by name."""
    # Some models return a string instead of a dict — normalize
    if isinstance(arguments, str):
        arguments = {"query": arguments, "text": arguments,
                     "key": arguments, "value": arguments, "category": "general"}

    if name == "save_memory":
        _memory_store.save(
            category=arguments.get("category", "general"),
            key=arguments.get("key", ""),
            value=arguments.get("text", ""),
        )
        return f"Saved [{arguments.get('category')}]: {arguments.get('key')}"

    if name == "search_memory":
        results = _memory_store.search(arguments.get("query", ""))
        if not results:
            return "No relevant memories found."
        lines = [f"[{r['category']}] {r['key']}: {r['value']}" for r in results]
        return "Found memories:\n" + "\n".join(lines)

    if name == "save_preference":
        _memory_store.save(
            category="preferences",
            key=arguments.get("key", ""),
            value=arguments.get("value", ""),
        )
        return f"Preference saved: {arguments.get('key')} = {arguments.get('value')}"

    return f"Unknown memory tool: {name}"
