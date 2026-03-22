# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""code-review: Review code changes and provide actionable feedback.

Usage: pipewright run code-review ./src/auth.py
       pipewright run code-review HEAD~1..HEAD
       pipewright run code-review #42
"""
from pipewright.workflow import Workflow, Step


class CodeReviewWorkflow(Workflow):
    name = "code-review"
    description = "Review code changes and provide actionable feedback"

    steps = [
        Step(
            name="gather-changes",
            prompt=(
                "Gather the code changes from {target}. "
                "If target is a file path, read the file. "
                "If target looks like a git ref (e.g., HEAD~1..HEAD, main..feature), run git diff. "
                "If target starts with '#', fetch the PR using gh pr diff. "
                "Output the changes with file paths and line numbers for context. "
                "Keep the output focused — only include the actual changes, not full files.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Bash", "Read", "Glob"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="analyze-quality",
            prompt=(
                "Perform a deep code quality analysis on the changes gathered from {target}. "
                "Search memory for any project-specific coding standards or past review patterns first. "
                "Identify:\n"
                "- BUGS: Logic errors, null/undefined access, off-by-one errors, race conditions\n"
                "- SECURITY: SQL injection, XSS, insecure dependencies, credential exposure, auth bypass\n"
                "- PERFORMANCE: N+1 queries, unnecessary loops, memory leaks, blocking operations\n"
                "- READABILITY: Complex logic, poor naming, missing docs, inconsistent style\n"
                "For each issue, note the specific file and line number. "
                "Focus on real problems — not style nitpicks unless they harm readability.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Grep", "Glob"],
            checkpoint=False,
            model="sonnet",
        ),
        Step(
            name="check-patterns",
            prompt=(
                "Check if the changes from {target} follow project conventions. "
                "Analyze the surrounding codebase to understand patterns for:\n"
                "- Naming conventions (camelCase, snake_case, PascalCase)\n"
                "- File structure and organization\n"
                "- Error handling patterns (try/catch, Result types, error codes)\n"
                "- Testing patterns (if tests were modified/added)\n"
                "- Import/dependency patterns\n"
                "Output only deviations from established patterns. "
                "If changes are consistent with the codebase, say so.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Grep", "Glob"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="synthesize-review",
            prompt=(
                "Synthesize a structured code review for {target} based on all prior analysis. "
                "Format the review as follows:\n\n"
                "## Summary\n"
                "<1-2 sentence overview of changes and overall quality>\n\n"
                "## Critical Issues\n"
                "<Bugs, security, major performance problems — include file:line references>\n\n"
                "## Warnings\n"
                "<Readability issues, minor performance concerns, pattern deviations>\n\n"
                "## Suggestions\n"
                "<Optional improvements, refactoring opportunities, best practices>\n\n"
                "## Actionable Fixes\n"
                "<For each critical/warning, provide a concrete fix with code examples>\n\n"
                "Be specific, constructive, and actionable. "
                "If no issues were found, say so clearly. "
                "Save any useful review patterns or project conventions to memory for future reviews.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Grep"],
            checkpoint=True,
            model="sonnet",
        ),
    ]
