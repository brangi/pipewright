# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the code-review workflow plugin."""
from pathlib import Path
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Workflow, Step


def test_code_review_discovered():
    """Plugin loader finds code-review alongside other workflows."""
    workflows = discover_plugins(Path("plugins"))
    assert "code-review" in workflows
    assert "test-gen" in workflows
    assert "issue-solve" in workflows


def test_code_review_is_workflow_subclass():
    """CodeReviewWorkflow is a proper Workflow subclass."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    assert isinstance(wf, Workflow)


def test_code_review_has_four_steps():
    """Workflow defines exactly 4 steps."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    assert len(wf.steps) == 4


def test_step_names():
    """Steps have the expected names in order."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    names = [s.name for s in wf.steps]
    assert names == ["gather-changes", "analyze-quality", "check-patterns", "synthesize-review"]


def test_checkpoints():
    """Only the final synthesize-review step has a checkpoint."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    checkpoints = [s.checkpoint for s in wf.steps]
    assert checkpoints == [False, False, False, True]


def test_model_assignments():
    """Haiku for cheap steps (gather, check-patterns), sonnet for analysis and synthesis."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    models = [s.model for s in wf.steps]
    assert models == ["haiku", "sonnet", "haiku", "sonnet"]


def test_prompts_contain_template_vars():
    """Every step prompt uses {target} and {context} placeholders."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    for step in wf.steps:
        assert "{target}" in step.prompt, f"Step '{step.name}' missing {{target}}"
        assert "{context}" in step.prompt, f"Step '{step.name}' missing {{context}}"


def test_gather_changes_has_bash_tool():
    """Step 1 needs Bash to run git diff or gh pr diff."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    assert "Bash" in wf.steps[0].tools


def test_gather_changes_has_read_tool():
    """Step 1 needs Read to access file contents."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    assert "Read" in wf.steps[0].tools


def test_analyze_quality_has_read_and_grep():
    """Step 2 needs Read and Grep to analyze code."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    analyze = wf.steps[1]
    assert "Read" in analyze.tools
    assert "Grep" in analyze.tools


def test_check_patterns_has_read_and_grep():
    """Step 3 needs Read and Grep to check conventions."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    check = wf.steps[2]
    assert "Read" in check.tools
    assert "Grep" in check.tools


def test_synthesize_review_has_read_and_grep():
    """Step 4 needs Read and Grep for final review synthesis."""
    workflows = discover_plugins(Path("plugins"))
    wf = workflows["code-review"]
    synthesize = wf.steps[3]
    assert "Read" in synthesize.tools
    assert "Grep" in synthesize.tools
