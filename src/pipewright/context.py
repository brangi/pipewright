# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Context compaction for inter-step communication.

Extracts structured summaries from step outputs instead of raw truncation.
Uses heuristic extraction (no LLM calls) to preserve key information.
"""
import re

_FILE_PATTERN = re.compile(
    r'(?:^|\s)((?:[a-zA-Z_./][\w./\-]*\.'
    r'(?:py|js|ts|tsx|rs|go|java|rb|c|cpp|h|md|json|yaml|yml|toml|css|html|sh))'
    r'|(?:/[\w./\-]+))',
)

_DECISION_WORDS = frozenset({
    "should", "must", "will", "decided", "recommend", "suggest",
    "created", "modified", "deleted", "changed", "added", "removed",
    "error", "warning", "fail", "pass", "success", "found", "missing",
})


def compact(text: str, limit: int = 800) -> str:
    """Extract a structured compact summary from step output.

    Uses heuristics to preserve the most useful information:
    1. File paths mentioned in the output
    2. Section headers (markdown or ALL CAPS)
    3. Lines containing decision/action/error keywords
    4. Head/tail of raw text as fallback

    Args:
        text: Raw step output text.
        limit: Maximum characters for the compact summary.

    Returns:
        Compact summary string, always under ``limit`` chars.
    """
    if not text or len(text) <= limit:
        return text

    lines = text.splitlines()
    sections: list[str] = []

    # 1. File paths
    files: list[str] = []
    for line in lines:
        for m in _FILE_PATTERN.finditer(line):
            f = m.group(1).strip()
            if f and f not in files and len(f) > 3:
                files.append(f)
    if files:
        sections.append("Files: " + ", ".join(files[:10]))

    # 2. Headers and key decision lines
    key_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Markdown headers
        if stripped.startswith("#"):
            if stripped not in seen:
                key_lines.append(stripped)
                seen.add(stripped)
            continue
        # ALL CAPS section labels (3-60 chars)
        if stripped.isupper() and 3 < len(stripped) < 60:
            if stripped not in seen:
                key_lines.append(stripped)
                seen.add(stripped)
            continue
        # Lines with decision/action keywords
        lower = stripped.lower()
        if any(w in lower for w in _DECISION_WORDS):
            if stripped not in seen:
                key_lines.append(stripped)
                seen.add(stripped)

    if key_lines:
        sections.append("\n".join(key_lines[:15]))

    # 3. Assemble summary
    summary = "\n".join(sections)

    # Fill remaining space with head/tail of raw text (only when no
    # structured content was extracted — avoids reintroducing duplicates)
    if len(summary) < limit - 100 and not key_lines and not files:
        remaining = limit - len(summary) - 20
        half = remaining // 2
        if half > 0:
            summary += f"\n---\n{text[:half]}\n...\n{text[-half:]}"

    # Safety net
    if len(summary) > limit:
        summary = summary[:limit - 3] + "..."

    return summary
