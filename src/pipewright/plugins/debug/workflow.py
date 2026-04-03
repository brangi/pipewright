# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""debug: Systematic debugging of an issue.

Usage: pipewright run debug "TypeError in auth.py line 42"
       pipewright run debug ./src/auth.py
"""
from pipewright.workflow import Workflow, Step


class DebugWorkflow(Workflow):
    name = "debug"
    description = "Systematic debugging: reproduce, analyze, fix"

    steps = [
        Step(
            name="reproduce-issue",
            prompt=(
                "Attempt to reproduce the issue described by {target}. "
                "If target is a file path, read the file and look for obvious errors. "
                "If target is an error description, search the codebase for relevant code.\n"
                "Steps:\n"
                "- Read relevant source files\n"
                "- Check for recent changes (git log, git diff) that might have introduced the bug\n"
                "- Try to run the failing code or test to confirm the error\n"
                "- Document the exact error message, stack trace, and reproduction steps\n"
                "Search memory for any known issues or debugging patterns first.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep", "Bash"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="analyze-root-cause",
            prompt=(
                "Analyze the root cause of the issue related to {target}. "
                "Based on the reproduction from the previous step:\n"
                "- Trace the execution path that leads to the error\n"
                "- Identify the exact line(s) of code causing the problem\n"
                "- Determine WHY the code fails\n"
                "- Check if this is a regression\n"
                "- Identify any related issues that share the same root cause\n"
                "Output a clear ROOT CAUSE statement.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep", "Bash"],
            checkpoint=False,
            model="sonnet",
        ),
        Step(
            name="propose-fix",
            prompt=(
                "Propose a fix for the issue in {target} based on the root cause analysis. "
                "For each change:\n"
                "FILE: <file path>\n"
                "LINE: <line number or range>\n"
                "CURRENT: <current code>\n"
                "PROPOSED: <fixed code>\n"
                "EXPLANATION: <why this fixes the root cause>\n\n"
                "Also propose a regression test that would catch this bug. "
                "Keep the fix minimal.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=True,
            model="sonnet",
        ),
        Step(
            name="apply-fix",
            prompt=(
                "Apply the proposed fix for the issue in {target}. "
                "Follow the fix from the previous step exactly. "
                "If the user provided feedback at the checkpoint, incorporate it.\n"
                "Steps:\n"
                "1. Apply each code change from the proposal\n"
                "2. Write or update a regression test\n"
                "3. Run the test to verify the fix works\n"
                "4. Run related tests to check for regressions\n\n"
                "After applying:\n"
                "FILES CHANGED: <list of modified files>\n"
                "TEST RESULT: <pass/fail and details>\n"
                "Save the debugging pattern to memory.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            checkpoint=True,
            model="sonnet",
        ),
    ]
