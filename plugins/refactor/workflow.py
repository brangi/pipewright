# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""refactor: Refactor code for better readability, performance, and maintainability.

Usage: pipewright run refactor ./src/auth.py
       pipewright run refactor ./src/
"""
from pipewright.workflow import Workflow, Step


class RefactorWorkflow(Workflow):
    name = "refactor"
    description = "Refactor code for better readability, performance, and maintainability"

    steps = [
        Step(
            name="analyze-code",
            prompt=(
                "Analyze the code at {target} to understand its structure and purpose. "
                "Read the target file(s) and surrounding codebase. Identify:\n"
                "- Current code structure and patterns\n"
                "- Dependencies and imports\n"
                "- Code smells: long functions, deep nesting, duplication, unclear naming\n"
                "- Test coverage (check if tests exist for this code)\n"
                "Search memory for any project-specific refactoring preferences first.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="identify-improvements",
            prompt=(
                "Based on the code analysis of {target}, identify specific improvements. "
                "Categorize each improvement:\n"
                "- READABILITY: naming, structure, comments, complexity reduction\n"
                "- PERFORMANCE: algorithm improvements, unnecessary allocations, caching\n"
                "- MAINTAINABILITY: separation of concerns, DRY violations, coupling\n"
                "- SAFETY: error handling, type hints, edge cases\n"
                "For each improvement, explain the current problem and the proposed fix. "
                "Prioritize by impact.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="plan-refactor",
            prompt=(
                "Create a detailed refactoring plan for {target} based on the improvements identified. "
                "For each change:\n"
                "FILE: <file path>\n"
                "CHANGE: <description of what to change>\n"
                "BEFORE: <current code pattern>\n"
                "AFTER: <proposed code pattern>\n"
                "RISK: low/medium/high\n\n"
                "Order changes to minimize risk. Flag any changes that could break existing tests.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=True,
            model="sonnet",
        ),
        Step(
            name="apply-changes",
            prompt=(
                "Apply the refactoring plan to {target}. Follow the plan from the previous step exactly. "
                "If the user provided feedback at the checkpoint, incorporate it.\n"
                "Rules:\n"
                "- Make one logical change at a time\n"
                "- Preserve all existing behavior (this is refactoring, not feature work)\n"
                "- Update imports and references as needed\n"
                "- Do not modify tests unless they test internal implementation details\n"
                "After making changes, output:\n"
                "FILES CHANGED: <list of modified files>\n"
                "CHANGES APPLIED: <summary of each change>\n"
                "Save useful refactoring patterns to memory.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            checkpoint=True,
            model="sonnet",
        ),
    ]
