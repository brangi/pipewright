# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

"""Tests for the debug workflow plugin."""
from pathlib import Path
from pipewright.plugins.loader import discover_plugins
from pipewright.workflow import Workflow


def test_debug_discovered():
    workflows = discover_plugins(Path("plugins"))
    assert "debug" in workflows


def test_debug_is_workflow_subclass():
    workflows = discover_plugins(Path("plugins"))
    assert isinstance(workflows["debug"], Workflow)


def test_debug_has_four_steps():
    workflows = discover_plugins(Path("plugins"))
    assert len(workflows["debug"].steps) == 4


def test_step_names():
    workflows = discover_plugins(Path("plugins"))
    names = [s.name for s in workflows["debug"].steps]
    assert names == ["reproduce-issue", "analyze-root-cause", "propose-fix", "apply-fix"]


def test_checkpoints():
    workflows = discover_plugins(Path("plugins"))
    checkpoints = [s.checkpoint for s in workflows["debug"].steps]
    assert checkpoints == [False, False, True, True]


def test_model_assignments():
    workflows = discover_plugins(Path("plugins"))
    models = [s.model for s in workflows["debug"].steps]
    assert models == ["haiku", "sonnet", "sonnet", "sonnet"]


def test_prompts_contain_template_vars():
    workflows = discover_plugins(Path("plugins"))
    for step in workflows["debug"].steps:
        assert "{target}" in step.prompt, f"Step '{step.name}' missing {{target}}"
        assert "{context}" in step.prompt, f"Step '{step.name}' missing {{context}}"


def test_reproduce_has_bash_tool():
    workflows = discover_plugins(Path("plugins"))
    assert "Bash" in workflows["debug"].steps[0].tools


def test_apply_fix_has_write_edit_bash_tools():
    workflows = discover_plugins(Path("plugins"))
    apply_step = workflows["debug"].steps[3]
    assert "Write" in apply_step.tools
    assert "Edit" in apply_step.tools
    assert "Bash" in apply_step.tools
