# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the issue-solve workflow plugin."""
from pathlib import Path
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Workflow, Step


def test_issue_solve_discovered():
    """Plugin loader finds issue-solve alongside test-gen."""
    workflows = discover_plugins(Path("plugins"))
    assert "issue-solve" in workflows
    assert "test-gen" in workflows


def test_issue_solve_is_workflow_subclass():
    """IssueSolveWorkflow is a proper Workflow subclass."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    assert isinstance(wf, Workflow)


def test_issue_solve_has_five_steps():
    """Workflow defines exactly 5 steps."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    assert len(wf.steps) == 5


def test_step_names():
    """Steps have the expected names in order."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    names = [s.name for s in wf.steps]
    assert names == ["fetch-issue", "analyze-codebase", "plan", "implement", "commit-and-pr"]


def test_checkpoints():
    """Steps 3, 4, 5 have checkpoints; steps 1, 2 do not."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    checkpoints = [s.checkpoint for s in wf.steps]
    assert checkpoints == [False, False, True, True, True]


def test_model_assignments():
    """Haiku for cheap steps, sonnet for planning and implementation."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    models = [s.model for s in wf.steps]
    assert models == ["haiku", "haiku", "sonnet", "sonnet", "haiku"]


def test_prompts_contain_template_vars():
    """Every step prompt uses {target} and {context} placeholders."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    for step in wf.steps:
        assert "{target}" in step.prompt, f"Step '{step.name}' missing {{target}}"
        assert "{context}" in step.prompt, f"Step '{step.name}' missing {{context}}"


def test_fetch_issue_has_bash_tool():
    """Step 1 needs Bash to run gh CLI."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    assert "Bash" in wf.steps[0].tools


def test_implement_has_write_and_edit_tools():
    """Step 4 needs Write and Edit to modify code."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    implement = wf.steps[3]
    assert "Write" in implement.tools
    assert "Edit" in implement.tools


def test_commit_step_has_bash_tool():
    """Step 5 needs Bash for git and gh commands."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["issue-solve"]
    assert "Bash" in wf.steps[4].tools
