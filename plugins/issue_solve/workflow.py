# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""issue-solve: Solve GitHub issues end-to-end.

Usage: pipewright run issue-solve 42
       pipewright run issue-solve #42
"""
from pipewright.workflow import Workflow, Step


class IssueSolveWorkflow(Workflow):
    name = "issue-solve"
    description = "Solve GitHub issues end-to-end: fetch, analyze, plan, implement, PR"

    steps = [
        Step(
            name="fetch-issue",
            prompt=(
                "Fetch GitHub issue {target} using the gh CLI. "
                "If the target starts with '#', strip it first. "
                "Run: gh issue view <number> --json title,body,labels,assignees,comments,state,milestone\n"
                "If the --json flag fails, fall back to: gh issue view <number>\n"
                "Output a structured summary with these sections at the top:\n"
                "ISSUE NUMBER: <number>\n"
                "TITLE: <title>\n"
                "LABELS: <labels>\n"
                "BODY: <body text>\n"
                "Keep the summary concise — it will be truncated to 1000 chars for later steps.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Bash"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="analyze-codebase",
            prompt=(
                "Based on GitHub issue {target} below, explore the codebase to understand "
                "what code is relevant to solving it. Search for keywords from the issue "
                "title and body. Identify:\n"
                "- Relevant source files and their purpose\n"
                "- Testing framework in use (if any)\n"
                "- Key dependencies or patterns\n"
                "Focus only on areas related to the issue — do not explore the entire codebase.\n"
                "Output a concise summary with RELEVANT FILES listed first.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep", "Bash"],
            checkpoint=False,
            model="haiku",
        ),
        Step(
            name="plan",
            prompt=(
                "Based on the issue details and codebase analysis below, create an "
                "implementation plan to solve this issue. Include:\n"
                "BRANCH: issue-{target}/<short-description> (strip # from target if present)\n"
                "FILES TO MODIFY: list each file with specific changes\n"
                "FILES TO CREATE: list any new files needed\n"
                "APPROACH: brief description of the solution\n"
                "Keep the plan concise and actionable. The user will review it at a checkpoint "
                "before any code is written. Front-load the BRANCH name and file list — "
                "they must appear in the first 500 characters of your output.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Glob", "Grep"],
            checkpoint=True,
            model="sonnet",
        ),
        Step(
            name="implement",
            prompt=(
                "Implement the plan from the previous step to solve GitHub issue {target}. "
                "Follow the plan exactly. If the user provided feedback at the checkpoint, "
                "incorporate it.\n"
                "Rules:\n"
                "- Make minimal, focused changes — no unrelated refactoring\n"
                "- Do not modify .env files or credentials\n"
                "- Run quick sanity checks (syntax, imports) but not the full test suite\n"
                "After making changes, output a summary starting with:\n"
                "FILES CHANGED: <list of files you modified or created>\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            checkpoint=True,
            model="sonnet",
        ),
        Step(
            name="commit-and-pr",
            prompt=(
                "Create a branch, commit, and open a PR for the changes made in the previous step.\n"
                "Steps:\n"
                "1. Check git status — if the working tree is clean, report that and stop\n"
                "2. Create and switch to branch (get name from the plan in context)\n"
                "3. Stage the specific files that were changed (from FILES CHANGED in context). "
                "Never stage .env, credentials, or secrets.\n"
                "4. Commit with message: 'Fix <title> (#{target})' (strip # from target if present)\n"
                "5. Push the branch: git push -u origin <branch-name>\n"
                "6. Open PR: gh pr create --title '<title>' --body 'Closes #{target}\\n\\n<summary>'\n"
                "If push or PR creation fails (no remote, auth issues), report the error "
                "clearly but keep the local branch and commit intact.\n\n"
                "Context from prior steps:\n{context}"
            ),
            tools=["Bash", "Read"],
            checkpoint=True,
            model="haiku",
        ),
    ]
